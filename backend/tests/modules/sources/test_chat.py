"""src.chat: per-message documents from the dev chat exports; synthetic exports cover the edges.

Hold-out exports (ROM01) are never opened here: scope tests only check that they stay out.
"""

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from tessera.core.contracts import ModuleSnapshot, RunSpec, Segment, SourceDocument
from tessera.core.db import connect
from tessera.core.orchestrator import run
from tessera.core.registry import RegisteredModule, Registry
from tessera.core.run_repo import repo_session
from tessera.modules.sources import chat
from tessera.modules.sources.chat import EXPORTS, MANIFEST, Export, collect, parse, teams_text

ROOT = Path(__file__).resolve().parents[4]
SOURCES = ROOT / "generated" / "sources"
ROME = ZoneInfo("Europe/Rome")
SEOUL = ZoneInfo("Asia/Seoul")
END = datetime(2026, 10, 22, 23, 59, tzinfo=UTC)


def spec(stores, as_of):
    return RunSpec(
        run_id="chat-run",
        scenario_id="historical",
        as_of=as_of,
        stores=tuple(stores),
        source_manifest_hash="sources",
        config_hash="config",
        code_version="test",
        mode="live",
        # Disabled by default: a run enables it explicitly.
        modules=(
            ModuleSnapshot(manifest=MANIFEST.model_copy(update={"enabled": True}), params={}),
        ),
        prompt_versions={},
        model_versions={},
        authorized_fixture_refs=(),
    )


def synthetic(tmp_path, files):
    """A sources dir with the real master data and only the given chat exports."""
    master = tmp_path / "erp" / "master_data"
    master.mkdir(parents=True)
    shutil.copy(SOURCES / "erp" / "master_data" / "stores.csv", master / "stores.csv")
    root = tmp_path / "internal_comms" / "chat_exports"
    root.mkdir(parents=True)
    for name, text in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text, encoding="utf-8")
    return tmp_path


def test_registry_discovers_src_chat_disabled_by_default():
    assert MANIFEST in Registry.discover().manifests()
    assert MANIFEST.enabled is False


def test_whatsapp_android_locales_and_system_lines():
    it = parse(
        "01/09/26, 08:12 - I messaggi sono crittografati end-to-end.\n"
        "01/09/26, 08:47 - Marco: Buongiorno: consegna alle 10\n"
        "seconda riga\n",
        "whatsapp",
        ROME,
    )
    assert it.unparsed == []
    system, message = it.messages
    assert system.author is None
    assert message.author == "Marco"
    assert message.text == "Buongiorno: consegna alle 10\nseconda riga"
    assert message.at == datetime(2026, 9, 1, 8, 47, tzinfo=ROME)
    es = parse("1/9/26, 09:41 - Lucía: hola\n", "whatsapp", ROME).messages[0]
    fr = parse("31/08/2026 09:05 - Camille: bonjour\n", "whatsapp", ROME).messages[0]
    assert es.at == datetime(2026, 9, 1, 9, 41, tzinfo=ROME)
    assert fr.at == datetime(2026, 8, 31, 9, 5, tzinfo=ROME)


def test_whatsapp_ios_seconds_and_attachment_marks():
    parsed = parse(
        "[04/09/26, 13:15:22] Anna: ‎<attached: 00000001-PHOTO-2026-09-04-13-15-22.jpg>\n"
        "[04/09/26, 13:16:01] Anna: cantiere davanti\n",
        "whatsapp_ios",
        ROME,
    )
    photo, text = parsed.messages
    assert chat.drop_reason(photo) == "media_only"
    assert text.at == datetime(2026, 9, 4, 13, 16, 1, tzinfo=ROME)
    assert chat.drop_reason(text) is None


def test_kakaotalk_twelve_hour_clock():
    parsed = parse(
        "점장방 님과 카카오톡 대화\n저장한 날짜 : 2026-10-22 09:14:52\n\n"
        "--------------- 2026년 9월 1일 화요일 ---------------\n"
        "[김지현] [오전 12:05] 자정\n"
        "[김지현] [오후 12:30] 점심\n"
        "[박민수] [오후 6:22] 사진\n",
        "kakaotalk",
        SEOUL,
    )
    midnight, noon, photo = parsed.messages
    assert midnight.at == datetime(2026, 9, 1, 0, 5, tzinfo=SEOUL)
    assert noon.at == datetime(2026, 9, 1, 12, 30, tzinfo=SEOUL)
    assert chat.drop_reason(photo) == "media_only"


def test_line_crlf_and_call_records():
    parsed = parse(
        "[LINE] 店長会のトーク履歴\r\n保存日時：2026/10/22 9:20\r\n\r\n"
        "2026/09/02(水)\r\n21:05\t高橋 由香\t今日も34℃\r\n21:30\t☎ 通話時間 12:04\r\n",
        "line",
        ZoneInfo("Asia/Tokyo"),
    )
    message, call = parsed.messages
    assert (message.author, message.text) == ("高橋 由香", "今日も34℃")
    assert chat.drop_reason(call) == "system"


def test_wechat_multiline_and_recalled():
    parsed = parse(
        "微信群聊记录导出\n导出时间：2026-10-22\n消息总数：2\n====\n\n"
        "2026-10-05 19:04:11 陈浩\n终于来了。\nSHA01 已经15件了\n\n"
        "2026-10-06 13:15:42 杨帆\n撤回了一条消息\n\n"
        '2026-10-06 13:20:00 杨帆\n[语音] 23"\n',
        "wechat",
        ZoneInfo("Asia/Shanghai"),
    )
    first, recalled, voice = parsed.messages
    assert first.text == "终于来了。\nSHA01 已经15件了"
    assert chat.drop_reason(recalled) == "deleted"
    assert chat.drop_reason(voice) == "media_only"


def test_teams_html_mentions_replies_and_deletions():
    def message(id_, at, content, reply_to=None, deleted=None):
        return {
            "id": id_,
            "replyToId": reply_to,
            "messageType": "message",
            "createdDateTime": at,
            "deletedDateTime": deleted,
            "from": {"user": {"displayName": "Luca"}},
            "body": {"contentType": "html", "content": content},
            "attachments": [{"name": "alloc.xlsx", "contentUrl": "https://private"}],
        }

    export = {
        "value": [
            {
                **message("1", "2026-09-07T07:05:08.444Z", "<p>by <b>Wed</b> &amp; Fri</p>"),
                "replies": [
                    message("2", "2026-09-07T08:02:31Z", '<p><at id="0">Priya</at> on it</p>', "1"),
                    message("3", "2026-09-07T09:00:00Z", "<p>x</p>", "1", "2026-09-07T09:01Z"),
                ],
            }
        ]
    }
    root, reply, deleted = parse(json.dumps(export), "teams", ZoneInfo("UTC")).messages
    assert root.text == "by Wed & Fri"
    assert root.at == datetime(2026, 9, 7, 7, 5, 8, 444000, tzinfo=UTC)
    assert root.attachments == ("alloc.xlsx",)
    assert (reply.text, reply.reply_to) == ("Priya on it", "1")
    assert chat.drop_reason(deleted) == "deleted"
    assert teams_text("<p>a</p><p>b<br>c</p>") == "a\nb\nc"


def test_dev_exports_parse_every_line_and_respect_scope():
    dev = ["MIL01", "MAD01", "PAR01", "SEL01", "TYO01", "SHA01", "LON01"]
    batch = collect(SOURCES, dev, END)
    assert batch.problems == []
    exports = {d.meta["export"] for d, _ in batch.documents}
    assert not any("ROM01" in name for name in exports)  # hold-out stays out of dev runs
    assert len(exports) == len(EXPORTS) - 1
    for document, segments in batch.documents:
        assert document.source_type == "chat_message"
        assert document.available_at <= END
        (segment,) = segments
        segment.validate_against(document)
        assert document.text == segment.text
        scope = document.meta["scope_store_ids"]
        assert ("store_id" in document.meta) == (len(scope) == 1)
    replies = [d for d, _ in batch.documents if d.parent_document_id]
    ids = {d.id for d, _ in batch.documents}
    assert replies and all(d.parent_document_id in ids for d in replies)


def test_single_store_run_reads_only_its_chats():
    batch = collect(SOURCES, ["MIL01"], END)
    assert {d.meta["export"] for d, _ in batch.documents} == {
        "Chat WhatsApp con MIL01 Team.txt",
        "Teams_RetailOpsEMEA_Stock-and-Transfers_export_20261022.json",
    }
    store_chat = [d for d, _ in batch.documents if d.meta.get("store_id")]
    assert {d.meta["store_id"] for d in store_chat} == {"MIL01"}


def test_messages_after_as_of_stay_out_and_ids_are_stable():
    early = datetime(2026, 9, 10, 20, 0, tzinfo=UTC)
    before = collect(SOURCES, ["MIL01"], early)
    after = collect(SOURCES, ["MIL01"], END)
    assert before.documents and len(before.documents) < len(after.documents)
    assert all(d.available_at <= early for d, _ in before.documents)
    later = {d.id: d for d, _ in after.documents}
    assert all(later[d.id] == d for d, _ in before.documents)


def test_unknown_exports_unparsed_lines_and_unicode_offsets(tmp_path):
    export = Export("store.txt", "whatsapp", "wa-test", ("MIL01",), "it")
    sources = synthetic(
        tmp_path,
        {
            "store.txt": "stray line\n02/09/26, 13:06 - Chiara: sushi 🍣 粉色 x2\n",
            "Signal export.txt": "whatever",
        },
    )
    batch = collect(sources, ["MIL01"], END, exports=(export,))
    uri = "dataset://internal_comms/chat_exports"
    assert batch.problems == [
        f"{uri}/Signal export.txt: unsupported chat export",
        f"{uri}/store.txt: line 1 is not a message",
    ]
    ((document, (segment,)),) = batch.documents
    assert document.id == "doc-chat-wa-test-1"
    assert document.business_date.isoformat() == "2026-09-02"
    assert segment.char_end == len("sushi 🍣 粉色 x2")
    assert document.source_refs[0].locator == "line:2"


def test_run_publishes_documents_and_reports_drops(tmp_path):
    as_of = datetime(2026, 10, 1, 20, 0, tzinfo=UTC)
    request = spec(["MAD01"], as_of)
    engine = connect(f"sqlite:///{tmp_path / 'chat.db'}")
    registry = Registry(
        (RegisteredModule(MANIFEST, lambda ctx: chat.run(ctx, sources_dir=SOURCES)),)
    )
    (status,) = run(request, engine=engine, registry=registry, clients={})
    assert status.status == "succeeded"
    counts = status.result.counts
    assert counts["documents"] == counts["segments"] > 0
    assert counts["dropped_system"] >= 1
    with repo_session(engine, request) as repo:
        documents = repo.list(SourceDocument)
        assert len(documents) == counts["documents"]
        assert len(repo.list(Segment)) == counts["segments"]
        assert all(d.available_at <= as_of for d in documents)
    engine.dispose()

import { createElement } from 'react'
import type { LucideIcon } from 'lucide-react'
import {
  ArrowLeftRight, BrainCircuit, Calculator, ChartLine, ChartSpline, CloudSun, Combine, CopyCheck, Database,
  FileSpreadsheet, FolderKanban, Inbox, Languages, Link2, Mail, MapPin, MessagesSquare, Mic, Newspaper, Puzzle,
  ScanText, Shirt, Sigma, Sparkles, TableProperties, Telescope, UserCheck, Warehouse
} from 'lucide-react'
import type { ModuleManifest } from '../api/client'
import { phases } from './moduleGraph'

// Display names and icons for the installed modules. The id stays visible next to the name:
// it is what manifests, traces and logs use. Unknown modules fall back to their id.
const catalog: Record<string, { title: string; icon: LucideIcon }> = {
  'src.email': { title: 'Email di chiusura', icon: Mail },
  'src.voice': { title: 'Note vocali', icon: Mic },
  'src.chat': { title: 'Chat dei negozi', icon: MessagesSquare },
  'src.docs': { title: 'Report Excel', icon: FileSpreadsheet },
  'src.erp': { title: 'ERP e vendite', icon: Database },
  'src.external': { title: 'Meteo ed eventi', icon: CloudSun },
  'sys.client': { title: 'Magazzino e logistica', icon: Warehouse },
  'ing.segment': { title: 'Segmenti e lingua', icon: Languages },
  'ing.extract': { title: 'Estrazione segnali', icon: ScanText },
  'ing.metrics': { title: 'Metriche dai report', icon: TableProperties },
  'int.link': { title: 'Collegamento prodotti', icon: Link2 },
  'int.dedup': { title: 'Deduplica', icon: CopyCheck },
  'int.cases': { title: 'Casi', icon: FolderKanban },
  'int.context': { title: 'Contesto esterno', icon: MapPin },
  'ins.product': { title: 'Insight prodotto', icon: Shirt },
  'fc.baseline': { title: 'Forecast di base', icon: ChartLine },
  'fc.overlay': { title: 'Scenari di domanda', icon: ChartSpline },
  'fc.residuals': { title: 'Residui storici', icon: Sigma },
  'act.options': { title: 'Opzioni di stock', icon: ArrowLeftRight },
  'ag.investigator': { title: 'Agente investigatore', icon: Telescope },
  'ag.analyst': { title: 'Agente analista', icon: BrainCircuit },
  'out.reports': { title: 'Brief per ufficio', icon: Newspaper }
}

export const phaseIcons: Record<string, LucideIcon> = {
  sources: Inbox,
  ingestion: ScanText,
  integration: Combine,
  intelligence: ChartSpline,
  decision: ArrowLeftRight,
  outputs: Newspaper
}
// Who does the work in each phase, as an icon beside the words.
export const actorIcons: Record<string, LucideIcon> = {
  sources: Database,
  ingestion: Sparkles,
  integration: Sparkles,
  intelligence: Calculator,
  decision: Calculator,
  outputs: UserCheck
}

export const moduleTitle = (id: string) => catalog[id]?.title ?? id
export const moduleIcon = (id: string, manifest: ModuleManifest | null): LucideIcon =>
  catalog[id]?.icon ?? (manifest ? phaseIcons[phaseOf(manifest.layer)] ?? Puzzle : Puzzle)
export const phaseOf = (layer: ModuleManifest['layer']) =>
  phases.find((phase) => phase.layers.includes(layer))?.key ?? 'sources'
/** 1-based slot of the phase colour (`--sd-phase-N`), in pipeline order. */
export const phaseSlot = (key: string) => phases.findIndex((phase) => phase.key === key) + 1

/** The module's icon as an element, so callers never pick a component during render. */
export const ModuleGlyph = ({ id, manifest }: { id: string; manifest: ModuleManifest | null }) =>
  createElement(moduleIcon(id, manifest), { 'aria-hidden': true })

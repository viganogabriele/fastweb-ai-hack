import snapshot from '../demo/online.json'
import { onlineCatalogMatch, onlineCountries, onlineForSku, onlineLabel, onlineProductHref, onlineSearches, onlineSizeBars, topOnlineProducts, formatOnlineCount, formatOnlineConversions } from './onlineData'
import type { OnlineData, OnlineProduct } from './onlineData'
import type { ProductCatalog } from './productsData'
import { useRunData } from './useRunData'
import './online.css'

const data: OnlineData = snapshot
const countingNote = 'In attesa: limite superiore delle iscrizioni attive. Conversioni n.d.: manca il timestamp per accertarle al cutoff.'

function OnlineMetrics({ product, stockouts }: { product: OnlineProduct; stockouts: number }) {
  return (
    <div className="sd-online__metrics">
      <dl className="sd-online__counts">
        <div><dt>Richieste</dt><dd>{formatOnlineCount(product.totalRequests)}</dd></div>
        <div><dt>In attesa</dt><dd>{formatOnlineCount(product.pending)}</dd></div>
        <div><dt>Convertite</dt><dd>{formatOnlineConversions(product.converted)}</dd></div>
        <div><dt>Eventi esaurimento</dt><dd>{formatOnlineCount(stockouts)}</dd></div>
      </dl>
      <div className="sd-online__sizes" role="group" aria-label="Richieste per taglia">
        {onlineSizeBars(product.bySize).map((row) => (
          <div key={row.size} className="sd-online__size">
            <span>{row.size}</span><span className="sd-online__track" aria-hidden="true"><span style={{ width: `${row.percent}%` }} /></span>
            <strong>{formatOnlineCount(row.requests)}</strong>
          </div>
        ))}
      </div>
      <p className="sd-online__countries">Paesi principali: {onlineCountries(product.topCountries).map((row) => `${row.country} · ${formatOnlineCount(row.requests)}`).join(' / ') || 'non disponibili'}</p>
    </div>
  )
}

export function OnlineDemand({ runId }: { runId: string }) {
  const catalog = useRunData<ProductCatalog>(runId, 'products')
  return (
    <div className="sd-online">
      <section className="sd-ov-panel sd-online__demand" aria-labelledby="online-demand">
        <header className="sd-ov-panel__head"><div><h2 id="online-demand">Domanda online</h2>
          <p>{onlineLabel(data.meta.cutoff)}</p>
          <p>Richieste di disponibilità dal {formatWindow(data.meta.requestWindowStart)}. Le richieste non sono vendite.</p>
          <p>{countingNote}</p>
        </div></header>
          <ol className="sd-online__products">
            {topOnlineProducts(data.topRequested).map((item) => {
              const match = catalog.data ? onlineCatalogMatch(catalog.data, item.sku) : null
              return <li key={item.sku}>
                <a className="sd-online__product" href={onlineProductHref(item.sku)}>
                  {match && <img src={match.product.image} alt="" loading="lazy" />}
                  <span><strong>{match?.product.name ?? item.styleName}</strong><span>{match?.colour.colour ?? item.colorName}</span>
                    {item.isNew && <span className="sd-online__new">Nuovo · senza storico</span>}
                  </span>
                </a>
                <OnlineMetrics product={item} stockouts={onlineForSku(data, item.sku).stockouts} />
              </li>
            })}
            {!data.topRequested.length && <li>Nessuna richiesta nel periodo.</li>}
          </ol>
      </section>
      <section className="sd-ov-panel sd-online__search" aria-labelledby="online-search">
        <header className="sd-ov-panel__head"><div><h2 id="online-search">Cercati sul sito e non trovati</h2>
          <p>{onlineLabel(data.meta.cutoff)}</p>
          <p>Ricerche senza risultati dal {formatWindow(data.meta.searchWindowStart)}.</p>
        </div></header>
        <div className="sd-online__searches">
          {onlineSearches(data.zeroResults).map((group) => <div key={group.country}>
            <h3>{group.country}</h3><ul>{group.terms.map((row) => <li key={row.term}><span>{row.term}</span><strong>{formatOnlineCount(row.searches)}<span className="sd-visually-hidden"> ricerche</span></strong></li>)}</ul>
          </div>)}
          {!data.zeroResults.length && <p>Nessuna ricerca senza risultati nel periodo.</p>}
        </div>
      </section>
    </div>
  )
}

function formatWindow(date: string) {
  return new Date(date).toLocaleDateString('it-IT', { day: '2-digit', month: '2-digit', timeZone: 'UTC' })
}

export function ProductOnline({ sku }: { sku: string | undefined }) {
  const signal = onlineForSku(data, sku)
  if (!signal.product) return null
  return <section className="sd-online-detail" aria-labelledby="sheet-online">
    <h3 id="sheet-online">Online</h3>
    <p className="sd-online__label">{onlineLabel(data.meta.cutoff)}</p>
    <p className="sd-online__label">{sku}</p>
    <>
      {signal.product.isNew && <p className="sd-online__new">Nuovo · senza storico</p>}
      <OnlineMetrics product={signal.product} stockouts={signal.stockouts} />
    </>
    <p className="sd-online__label">{countingNote}</p>
  </section>
}

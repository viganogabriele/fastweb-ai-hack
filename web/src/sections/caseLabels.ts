// Readable names for the RFC §4.3 owner enum; unknown values fall back to the raw id.
const owners: Record<string, string> = {
  allocation: 'Allocazione',
  retail_ops: 'Retail operations',
  product_quality: 'Qualità prodotto',
  merchandising: 'Merchandising',
  marketing: 'Marketing'
}
export const ownerLabel = (owner: string) => owners[owner] ?? owner.replaceAll('_', ' ')

const languages: Record<string, string> = { it: 'italiano', en: 'inglese', fr: 'francese', de: 'tedesco', es: 'spagnolo', ja: 'giapponese', ko: 'coreano', zh: 'cinese' }
export const languageLabel = (code: string | null | undefined) => (code ? languages[code] ?? code : null)

/** Short local date and time, for people: "23 ott, 09:00". */
export const shortDate = (value: string | null | undefined) =>
  value && Number.isFinite(Date.parse(value))
    ? new Date(value).toLocaleString('it-IT', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
    : null
export const shortDay = (value: string | null | undefined) =>
  value && Number.isFinite(Date.parse(value)) ? new Date(value).toLocaleDateString('it-IT', { day: 'numeric', month: 'short' }) : null

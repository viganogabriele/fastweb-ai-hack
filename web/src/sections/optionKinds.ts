import { ArrowLeftRight, BellRing, Layers, MessageCircleQuestion, PackageSearch, Pause, Truck, Warehouse } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'

// Readable names for the RFC action-option kinds, shared by the case options and the brief.
const kinds: Record<string, { label: string; icon: LucideIcon }> = {
  hold: { label: 'Mantieni lo stock attuale', icon: Pause },
  verify_stock: { label: 'Verifica lo stock in negozio', icon: PackageSearch },
  ask_store: { label: 'Chiedi conferma al negozio', icon: MessageCircleQuestion },
  replenish_dc: { label: 'Riassortisci dal magazzino', icon: Warehouse },
  transfer: { label: 'Trasferisci da un altro negozio', icon: Truck },
  combo: { label: 'Trasferimento combinato', icon: Layers },
  notify_owner: { label: 'Avvisa il responsabile', icon: BellRing }
}
export const optionKind = (kind: string) => kinds[kind] ?? { label: kind.replaceAll('_', ' '), icon: ArrowLeftRight }

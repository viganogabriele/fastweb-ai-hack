export function closeCitationAndRestoreFocus(
  trigger: Pick<HTMLElement, 'focus'> | null,
  closePanel: () => void
) {
  trigger?.focus()
  closePanel()
}

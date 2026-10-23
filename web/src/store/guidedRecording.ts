/** Staff codes are pseudonyms: trim outside whitespace and normalize ASCII case. */
export const normalizeStaffCode = (value: string) => value.trim().toLowerCase()
export const isValidStaffCode = (value: string) => /^[a-z0-9-]{1,32}$/.test(value) && value === value.trim()
export const canUseMicrophone = (staff: string, hasAccess: boolean, requesting: boolean) =>
  isValidStaffCode(staff) && hasAccess && !requesting
export const currentQuestion = (elapsedSeconds: number) => Math.floor(Math.max(0, elapsedSeconds) / 15) % 4
export const remainingTime = (elapsedSeconds: number) => {
  const seconds = Math.max(0, 90 - Math.floor(Math.max(0, elapsedSeconds)))
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`
}

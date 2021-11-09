export const truncateTitle = (title: string, maxLength = 50): string => (title.length > maxLength
  ? `${title.substring(0, maxLength)}…`
  : title);

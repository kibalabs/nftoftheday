export const truncateTitle = (title: string, maxLength = 50): string => {
  return (
    title.length > maxLength ? `${title.substring(0, maxLength)}…` : title);
};

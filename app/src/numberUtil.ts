export const numberWithCommas = (value: number): string => {
  if (value === null) {
    return '...';
  }
  return value.toString().replace(/\B(?<!\.\d*)(?=(\d{3})+(?!\d))/g, ',');
};

export const shortFormatNumber = (value: number): string => {
  if (value >= 1000000000) {
    return `${(value / 1000000000.0).toFixed(0)}B`;
  }
  if (value >= 10000000) {
    return `${(value / 1000000.0).toFixed(0)}M`;
  }
  if (value >= 1000000) {
    return `${(value / 1000000.0).toFixed(1)}M`;
  }
  if (value >= 10000) {
    return `${(value / 1000.0).toFixed(0)}K`;
  }
  if (value >= 1000) {
    return `${(value / 1000.0).toFixed(1)}K`;
  }
  if (value > 100) {
    return value.toFixed(0);
  }
  if (value > 1) {
    return value.toFixed(1);
  }
  return value.toFixed(2);
};

export const longFormatNumber = (value: number): string => {
  const roundedValue = value.toFixed(2);
  return `${roundedValue.toLocaleString()}`;
};

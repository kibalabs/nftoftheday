import { BigNumber } from 'ethers';

import { longFormatNumber, shortFormatNumber } from './numberUtil';

export const ETHER = BigNumber.from('1000000000000000000');

export const etherToNumber = (value: BigNumber): number => {
  return value.mul(1000).div(ETHER).toNumber() / 1000.0;
};

export const shortFormatEther = (value: BigNumber): string => {
  const numberString = shortFormatNumber(etherToNumber(value));
  return `Ξ${numberString}`;
};

export const longFormatEther = (value: BigNumber): string => {
  const numberString = longFormatNumber(etherToNumber(value));
  return `Ξ${numberString}`;
};

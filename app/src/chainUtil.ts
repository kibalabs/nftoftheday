import { BigNumber } from 'ethers';

import { longFormatNumber, shortFormatNumber } from './numberUtil';

const ETHER = BigNumber.from('1000000000000000000');

export const shortFormatEther = (value: BigNumber): string => {
  const numberString = shortFormatNumber(value.div(ETHER).toNumber());
  return `Ξ${numberString}`;
};

export const longFormatEther = (value: BigNumber): string => {
  const numberString = longFormatNumber(value.div(ETHER).toNumber());
  return `Ξ${numberString}`;
};

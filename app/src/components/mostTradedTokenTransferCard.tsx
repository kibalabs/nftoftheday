import React from 'react';

import { TradedToken } from '../client/resources';
import { NftCard } from './nftCard';

export type MostTradedTokenTransferCardProps = {
  tradedToken: TradedToken;
}

export const MostTradedTokenTransferCard = (props: MostTradedTokenTransferCardProps): React.ReactElement => {
  return (
    <NftCard
      label='Most Traded'
      subtitle={`Traded ${props.tradedToken.transferCount} times today`}
      primaryButtonText='View on OpenSea'
      primaryButtonTarget={`https://opensea.io/assets/${props.tradedToken.token.registryAddress}/${props.tradedToken.token.tokenId}?ref=0x18090cda49b21deaffc21b4f886aed3eb787d032`}
      secondaryButtonText='View Tx'
      secondaryButtonTarget={`https://etherscan.io/tx/${props.tradedToken.latestTransfer.transactionHash}`}
      token={props.tradedToken.token}
      collection={props.tradedToken.collection}
    />
  );
};

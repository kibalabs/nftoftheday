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
      primaryButtonText='View Token'
      secondaryButtonText='View Tx'
      secondaryButtonTarget={`https://etherscan.io/tx/${props.tradedToken.latestTransfer.transactionHash}`}
      token={props.tradedToken.token}
      collection={props.tradedToken.collection}
    />
  );
};

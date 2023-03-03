import React from 'react';

import { NftCard } from './nftCard';
import { TradedToken } from '../client/resources';

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

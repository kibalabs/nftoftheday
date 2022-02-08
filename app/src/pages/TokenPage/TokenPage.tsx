import React from 'react';

import { useRouteParams } from '@kibalabs/core-react';
import { Alignment, Direction, Stack, Text } from '@kibalabs/ui-react';


export const TokenPage = (): React.ReactElement => {
  const routeParams = useRouteParams();
  const registryAddress = routeParams.registryAddress as string;
  const tokenId = routeParams.tokenId as string;

  return (
    <Stack direction={Direction.Vertical} isFullWidth={true} isFullHeight={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Start} isScrollableVertically={true}>
      <Text variant='header3'>{`Token Page for ${registryAddress} ${tokenId}`}</Text>
    </Stack>
  );
};

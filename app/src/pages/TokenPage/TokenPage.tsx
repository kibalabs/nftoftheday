import React from 'react';

import { Alignment, Direction, Stack } from '@kibalabs/ui-react';


export const TokenPage = (): React.ReactElement => {
//   const routeParams = useRouteParams();
//   const address = routeParams.address as string;
//   const tokenId = routeParams.address as string;

  return (
    <Stack direction={Direction.Vertical} isFullWidth={true} isFullHeight={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Start} isScrollableVertically={true} />
  );
};

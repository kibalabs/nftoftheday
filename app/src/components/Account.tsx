import React from 'react';

import { truncateMiddle } from '@kibalabs/core';
import { Alignment, Box, Direction, Image, Stack, Text } from '@kibalabs/ui-react';

export interface AccountViewProps {
  accountId: string;
}
export const Account = (props: AccountViewProps): React.ReactElement => {
  return (
    <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true}>
      <Box variant='rounded-borderColored' shouldClipContent={true} height='20px' width='20px'>
        <Image source={`https://web3-images-api.kibalabs.com/v1/accounts/${props.accountId}/image`} alternativeText='Avatar' />
      </Box>
      <Text>{truncateMiddle(props.accountId, 10)}</Text>
    </Stack>
  );
};

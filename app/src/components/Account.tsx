import React from 'react';

import { truncateMiddle } from '@kibalabs/core';
import { Alignment, Box, Direction, Image, LinkBase, Stack, Text } from '@kibalabs/ui-react';

export interface AccountViewProps {
  accountId: string;
  target?: string;
}
export const Account = (props: AccountViewProps): React.ReactElement => {
  return (
    <LinkBase target={props.target}>
      <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true}>
        <Box variant='rounded' shouldClipContent={true} height='20px' width='20px'>
          <Image source={`https://web3-images-api.kibalabs.com/v1/accounts/${props.accountId}/image`} alternativeText='Avatar' />
        </Box>
        <Text>{truncateMiddle(props.accountId, 10)}</Text>
      </Stack>
    </LinkBase>
  );
};

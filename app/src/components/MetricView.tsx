import React from 'react';

import { Alignment, Box, Direction, PaddingSize, Stack, Text } from '@kibalabs/ui-react';

export interface MetricViewProps {
  name: string;
  value: number;
}

export const MetricView = (props: MetricViewProps): React.ReactElement => {
  return (
    <Box variant='card' height='100px' isFullWidth={true}>
      <Stack direction={Direction.Vertical} isFullHeight={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center}padding={PaddingSize.Wide2}>
        <Text variant='bold-large'>{props.value}</Text>
        <Text>{props.name}</Text>
      </Stack>
    </Box>
  );
};

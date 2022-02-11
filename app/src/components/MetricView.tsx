import React from 'react';

import { Alignment, Box, Direction, PaddingSize, Stack, Text, TextAlignment } from '@kibalabs/ui-react';

export interface MetricViewProps {
  name: string;
  value: string;
}

export const MetricView = (props: MetricViewProps): React.ReactElement => {
  return (
    <Box variant='metricCard' height='7rem' width='10rem'>
      <Stack direction={Direction.Vertical} isFullHeight={true} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} padding={PaddingSize.Default}>
        <Text alignment={TextAlignment.Center} variant='bold'>{props.value}</Text>
        <Text alignment={TextAlignment.Center} variant='small'>{props.name}</Text>
      </Stack>
    </Box>
  );
};

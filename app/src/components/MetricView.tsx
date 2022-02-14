import React from 'react';

import { Alignment, Box, Direction, PaddingSize, Stack, Text, TextAlignment } from '@kibalabs/ui-react';

export interface MetricViewProps {
  name: string;
  value: string;
}

export const MetricView = (props: MetricViewProps): React.ReactElement => {
  return (
    <Box variant='metricCard' height='5rem' width='7rem'>
      <Stack direction={Direction.Vertical} isFullHeight={true} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} padding={PaddingSize.Default}>
        <Text variant='bold' alignment={TextAlignment.Center} lineLimit={2}>{props.value}</Text>
        <Text variant='small' alignment={TextAlignment.Center} lineLimit={2}>{props.name}</Text>
      </Stack>
    </Box>
  );
};

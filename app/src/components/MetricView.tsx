import React from 'react';

import { Alignment, Box, Direction, PaddingSize, Stack, Text, TextAlignment } from '@kibalabs/ui-react';

export interface MetricViewProps {
  name: string;
  value: number;
}

export const MetricView = (props: MetricViewProps): React.ReactElement => {
  return (
    <Box variant='metricCard' height='100px'>
      <Stack direction={Direction.Vertical} isFullHeight={true} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} paddingHorizontal={PaddingSize.Wide}>
        <Text variant='bold-large'>{props.value}</Text>
        <Text variant='small' alignment={TextAlignment.Center}>{props.name}</Text>
      </Stack>
    </Box>
  );
};

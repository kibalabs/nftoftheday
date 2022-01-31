import React from 'react';

import { Alignment, Direction, Stack, Text } from '@kibalabs/ui-react';

export interface MetricViewProps {
  name: string;
  value: number;
}

export const MetricView = (props: MetricViewProps): React.ReactElement => {
  return (
    <Stack directionResponsive={{ base: Direction.Horizontal, medium: Direction.Vertical }} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center}>
      <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center}>
        <Text variant='bold-large'>{props.value}</Text>
      </Stack>
      <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center}>
        <Text>{props.name}</Text>
      </Stack>
    </Stack>
  );
};

import React from 'react';

import { Alignment, Box, Direction, PaddingSize, Spacing, Stack, Text } from '@kibalabs/ui-react';

export interface ErrorCardProps {
  label: string;
  extraLabelVariants?: string[];
  extraLabelBoxVariants?: string[];
  error?: Error;
}

export const ErrorCard = (props: ErrorCardProps): React.ReactElement => {
  const extraLabelVariantsString = props.extraLabelVariants ? `-${props.extraLabelVariants.join('-')}` : '';
  const extraLabelBoxVariantsString = props.extraLabelBoxVariants ? `-${props.extraLabelBoxVariants.join('-')}` : '';
  return (
    <Box variant='card'>
      <Stack direction={Direction.Vertical}>
        <Stack.Item alignment={Alignment.Start} gutterAfter={PaddingSize.Wide}>
          <Box variant={`cardLabelBox${extraLabelBoxVariantsString}`} isFullWidth={false}>
            <Text variant={`cardLabel${extraLabelVariantsString}`}>{props.label}</Text>
          </Box>
          <Spacing variant={PaddingSize.Wide} />
        </Stack.Item>
        <Stack direction={Direction.Vertical} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} paddingHorizontal={PaddingSize.Wide}>
          <Stack.Item alignment={Alignment.Start} gutterAfter={PaddingSize.Wide}>
            <Box width='175px' height='300px'>
              <Text variant='header3'>Sorry, Something went wrong.   </Text>
              <Spacing variant={PaddingSize.Wide} />
              <Text variant='header3'> Please Refresh the page.</Text>
            </Box>
          </Stack.Item>
          <Spacing variant={PaddingSize.Wide} />
        </Stack>
      </Stack>
    </Box>
  );
};

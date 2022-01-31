import React from 'react';

import { Alignment, Box, Button, Direction, MarkdownText, Stack, useTheme } from '@kibalabs/ui-react';

export interface TruncateTextProps {
  markdownText: string;
  maximumCharacters: number;
}

export const TruncateText = (props: TruncateTextProps): React.ReactElement => {
  const [shouldTruncateText, setShouldTruncateText] = React.useState<boolean>(true);
  const theme = useTheme();
  const onToggleClicked = () => {
    setShouldTruncateText(!shouldTruncateText);
  };
  return (
    <Stack direction={Direction.Vertical} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center}>
      <Box maxHeight={shouldTruncateText ? `calc(${theme.texts.default['line-height']} * 3)` : undefined} shouldClipContent={true}>
        <MarkdownText source={props.markdownText} />
      </Box>
      {shouldTruncateText ? (
        <Button variant='small' text={'read more'} onClicked={onToggleClicked} />
      ) : (
        <Button variant='small' text={'read less'} onClicked={onToggleClicked} />
      )}
    </Stack>
  );
};

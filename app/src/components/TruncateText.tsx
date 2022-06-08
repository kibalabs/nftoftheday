import React from 'react';

import { Alignment, Box, Button, Direction, MarkdownText, Stack, TextAlignment, useTheme } from '@kibalabs/ui-react';

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
    <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} contentAlignment={Alignment.Center}>
      <Box maxHeight={shouldTruncateText ? `calc(${theme.texts.default['line-height']} * 3)` : undefined} shouldClipContent={true}>
        <MarkdownText textAlignment={TextAlignment.Center} source={props.markdownText} />
      </Box>
      {props.markdownText.length >= props.maximumCharacters && (
        <Button variant='small' text={shouldTruncateText ? 'read more' : 'read less'} onClicked={onToggleClicked} />
      )}
    </Stack>
  );
};

import React from 'react';

import { Alignment, Button, Direction, MarkdownText, Stack } from '@kibalabs/ui-react';

export interface TruncateTextProps {
  markdownText: string;
  maximumCharacters: number}

export const TruncateText = (props: TruncateTextProps): React.ReactElement => {
  const [shouldTruncateText, setShouldTruncateText] = React.useState<boolean>(true);
  const descriptionText = shouldTruncateText ? props.markdownText.substring(0, props.maximumCharacters) : props.markdownText;
  const handleButtonToggle = () => {
    setShouldTruncateText(!shouldTruncateText);
  };
  return (
    <Stack direction={Direction.Vertical} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center}>
      <MarkdownText textVariant='light' source={descriptionText} />
      {shouldTruncateText ? (
        <Button variant='small' text={'read more'} onClicked={handleButtonToggle} />
      ) : (
        <Button variant='small' text={'read less'} onClicked={handleButtonToggle} />
      )}
    </Stack>
  );
};

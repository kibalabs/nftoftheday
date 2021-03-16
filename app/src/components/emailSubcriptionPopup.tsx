import React from  'react';

import { Dialog, Direction, Stack, Spacing, Text, Alignment, TextAlignment, PaddingSize, KibaIcon, SingleLineInput, IconButton, Button } from '@kibalabs/ui-react';

interface EmailSubsriptionPopupProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmButtonText?: string;
  cancelButtonText?: string;
  inputPlaceholder: string;
  inputText: string;
  onInputValueChanged: (value: string) => void;
  onConfirmClicked: () => void;
  onCloseClicked: () => void;
};


export const EmailSubsriptionPopup = (props: EmailSubsriptionPopupProps): React.ReactElement => {

  const cancelButtonText = props.cancelButtonText || 'Cancel';
  const confirmButtonText = props.confirmButtonText || 'Confirm';

  return (
   <Dialog
    isOpen={props.isOpen}
    onCloseClicked={props.onCloseClicked}
   >
    <Stack direction={Direction.Vertical} paddingHorizontal={PaddingSize.Wide} paddingVertical={PaddingSize.Wide} shouldAddGutters={true} defaultGutter={PaddingSize.Wide}>
    <Stack direction={Direction.Horizontal} contentAlignment={Alignment.Fill} childAlignment={Alignment.Center} shouldAddGutters={true}>
          <Spacing />
          <Text variant='header3' alignment={TextAlignment.Center}>{props.title}</Text>
          {props.onCloseClicked && (
            <IconButton icon={<KibaIcon iconId='ion-close' />} onClicked={props.onCloseClicked} />
          )}
        </Stack>
        <Text alignment={TextAlignment.Center}>{props.message}</Text>
        <SingleLineInput inputWrapperVariant='dialogInput' placeholderText={props.inputPlaceholder} value={props.inputText} onValueChanged={props.onInputValueChanged} />
        <Stack.Item gutterBefore={PaddingSize.Default}>
            <Button variant='primary' onClicked={props.onConfirmClicked} text={confirmButtonText} />
        </Stack.Item>
    </Stack>
   </Dialog>
  )

}
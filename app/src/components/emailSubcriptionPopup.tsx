import React from 'react';

import { Alignment, Button, Dialog, Direction, Form, IconButton, KibaIcon, PaddingSize, SingleLineInput, Spacing, Stack, Text, TextAlignment } from '@kibalabs/ui-react';

import { useGlobals } from '../globalsContext';

interface EmailSubsriptionPopupProps {
  isOpen: boolean;
  onCloseClicked: () => void;
}


export const EmailSubsriptionPopup = (props: EmailSubsriptionPopupProps): React.ReactElement => {
  const { notdClient } = useGlobals();
  const [inputText, setInputText] = React.useState<string>('');
  const [isLoading, setIsLoading] = React.useState<boolean>(false);
  const [isSuccessfullySubscribed, setIsSuccessfullySubscribed] = React.useState<boolean>(false);
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);

  const onSubscribeClicked = (): void => {
    setIsLoading(true);
    setIsSuccessfullySubscribed(false);
    setErrorMessage(null);
    notdClient.subscribe(inputText).then((): void => {
      setIsLoading(false);
      setIsSuccessfullySubscribed(true);
    }).catch((error: unknown): void => {
      setErrorMessage((error as Error).message);
      // TODO(krishan711): show the error
      setIsLoading(false);
    });
  };

  return (
    <Dialog
      isOpen={props.isOpen}
      onCloseClicked={props.onCloseClicked}
    >
      <Stack direction={Direction.Vertical} paddingHorizontal={PaddingSize.Wide} paddingVertical={PaddingSize.Wide} shouldAddGutters={true} defaultGutter={PaddingSize.Wide}>
        <Stack direction={Direction.Horizontal} contentAlignment={Alignment.Fill} childAlignment={Alignment.Center} shouldAddGutters={true}>
          <Spacing />
          <Text variant='header3' alignment={TextAlignment.Center}>☀️ Join Us</Text>
          {props.onCloseClicked && (
            <IconButton icon={<KibaIcon iconId='ion-close' />} onClicked={props.onCloseClicked} />
          )}
        </Stack>
        <Text alignment={TextAlignment.Center}>Get a daily does of the best NTFs straight to your inbox 🚀</Text>
        <Form isLoading={isLoading} onFormSubmitted={onSubscribeClicked}>
          <Stack direction={Direction.Vertical} shouldAddGutters={true} defaultGutter={PaddingSize.Wide}>
            <SingleLineInput inputWrapperVariant='dialogInput' placeholderText={'Email'} value={inputText} onValueChanged={setInputText} />
            <Button variant='primary' buttonType='submit' text='Subscribe' />
          </Stack>
        </Form>
        { isSuccessfullySubscribed && (
          <Text alignment={TextAlignment.Center}>Awesome, you&apos;ll be hearing from us soon!</Text>
        )}
        { errorMessage && (
          <Text alignment={TextAlignment.Center}>{errorMessage}</Text>
        )}
      </Stack>
    </Dialog>
  );
};

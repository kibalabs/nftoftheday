import React from 'react';

import {Button} from '@kibalabs/ui-react';
import { EmailSubsriptionPopup } from './emailSubcriptionPopup';

export const DialogTest = (props): React.ReactElement => {
  
  const [isOpen, setIsOpen] = React.useState(false);
  const [inpText, setInpText] = React.useState('');

  return (
    <React.Fragment>
    <Button variant='primary' text='subscribe' onClicked={() => {setIsOpen(!isOpen)}}/>
    <EmailSubsriptionPopup 
      isOpen={isOpen}
      onCloseClicked={() => setIsOpen(false)}
      onConfirmClicked={() => console.log(inpText)}
      inputPlaceholder='Email'
      onInputValueChanged={setInpText}
      inputText={inpText}
      title='Join Us'
      message='Subscribe to get the latest news on NFTs'
      confirmButtonText='Subscribe'
    />
    </React.Fragment>
  );
}
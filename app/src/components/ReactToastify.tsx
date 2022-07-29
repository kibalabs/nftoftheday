
import React from 'react';

import { ToastContainer } from 'react-toastify';
import styled from 'styled-components';


const toastProps: Record<string, unknown> = {
  autoClose: 4000,
  position: 'top-right',
  icon: true,
  closeButton: false,
  style: {
    width: 'auto',
  },
  hideProgressBar: true,
  closeOnClick: false,
};

const StyledReactToastify = styled(ToastContainer)`
  .Toastify__toast {
    cursor: inherit;
    font-family: 'Circular';
    background: #fff;
    box-shadow: none;
    padding: 0;
    margin-bottom: 0.75em;
    min-height: 10px;
  }
  .Toastify__toast-body {
    padding: 30px;
    margin: 0;
  }
  .Toastify__toast--error {
    border: 1px solid #EB5757;
    border-radius: 50px !important;
    background: #F0F9FA !important;
}
// .Toastify__toast--error::before {
//   content: url("../assets/error-icon.svg");
//   position:relative; 
//   z-index:100000;
//   left:15px;
//   top:25px;
// }
.Toastify__toast--success {
  border: 5px solid #3A9EA5 !important;
  border-radius: 50px !important;
  background: #F0F9FA !important;
}
// .Toastify__toast--success::before {
//   content: url("../assets/check-icon.svg");
//   position:relative; 
//   z-index:100000;
//   left:15px;
//   top:25px;
// }
.Toastify__toast--warning {
  border: 1px solid #E78326  !important;
  border-radius: 50px !important;
  background: #FADFC5 !important;
`;

export const ReactToastify = (): React.ReactElement => {
  return (
    <StyledReactToastify {...toastProps} />
  );
};

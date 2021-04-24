import React from 'react';

import { Text, useResponsiveScreenSize } from "@kibalabs/ui-react";

export const NewThing = (props): React.ReactElement => {
  const responsiveScreenSize = useResponsiveScreenSize();
  return (
     <Text>{responsiveScreenSize}</Text>
  );
}
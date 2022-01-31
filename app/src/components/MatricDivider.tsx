import React from 'react';

import { Box, ResponsiveHidingView, ScreenSize } from '@kibalabs/ui-react';

export const MatricDivider = (): React.ReactElement => {
  return (
    <ResponsiveHidingView hiddenBelow={ScreenSize.Medium}>
      <Box variant='divider' height='70px' width='1px' />
    </ResponsiveHidingView>
  );
};

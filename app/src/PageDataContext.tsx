import React, { useContext, useState } from 'react';

import { IMultiAnyChildProps } from '@kibalabs/core-react';

interface IPageData {
  data: unknown | null | undefined;
  setData: (data: unknown | null | undefined) => void;
}

const PageDataContext = React.createContext<IPageData | null>(null);

interface IPageDataProviderProps extends IMultiAnyChildProps {
  initialData: unknown | null | undefined;
}

export const PageDataProvider = (props: IPageDataProviderProps) => {
  const [data, setData] = useState<unknown | null | undefined>(props.initialData);
  return (
    <PageDataContext.Provider value={{ data, setData }}>
      {props.children}
    </PageDataContext.Provider>
  );
};

export const usePageData = (): IPageData => {
  const pageDataContext = useContext(PageDataContext);
  if (!pageDataContext) {
    throw new Error('Cannot use usePageData since pageDataContext has not ben provided above in the hierarchy');
  }
  return pageDataContext;
};

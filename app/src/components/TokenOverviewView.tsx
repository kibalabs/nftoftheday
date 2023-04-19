import React from 'react';

import { shortFormatEther } from '@kibalabs/core';
import { Alignment, Box, Direction, LinkBase, Media, PaddingSize, Spacing, Stack, Text, TextAlignment } from '@kibalabs/ui-react';

import { CollectionToken } from '../client/resources';


export interface TokenOverviewViewProps {
  title: string;
  collectionToken: CollectionToken;
  value?: bigint
}


export const TokenOverviewView = (props: TokenOverviewViewProps): React.ReactElement => {
  const imageUrl = props.collectionToken.imageUrl || '/assets/icon.png';
  return (
    <LinkBase target={`/collections/${props.collectionToken.registryAddress}/tokens/${props.collectionToken.tokenId}`}>
      <Box variant='tokenOverviewViewCard' maxWidth='15rem' shouldClipContent={false}>
        <Stack direction={Direction.Vertical} isFullHeight={true} isFullWidth={true} childAlignment={Alignment.Start} contentAlignment={Alignment.Start} padding={PaddingSize.Default}>
          <Text variant='default' alignment={TextAlignment.Left} lineLimit={2}>{props.title}</Text>
          <Stack direction={Direction.Horizontal} paddingVertical={PaddingSize.Default}>
            <Box variant='rounded' height='2rem' width='2rem' shouldClipContent={true}>
              <Media source={imageUrl} alternativeText='image' fitType='cover' />
            </Box>
            <Stack contentAlignment={Alignment.Center} paddingLeft={PaddingSize.Default}>
              <Text variant='small' alignment={TextAlignment.Left} lineLimit={2} shouldBreakAnywhere={true}>{props.collectionToken.name}</Text>
              <Spacing variant={PaddingSize.Default} />
              { props.value != null && (
                <Text variant='small' lineLimit={2} alignment={TextAlignment.Left}>{`${shortFormatEther(BigInt(props.value.toString()))}`}</Text>
              )}
            </Stack>
          </Stack>
        </Stack>
      </Box>
    </LinkBase>
  );
};

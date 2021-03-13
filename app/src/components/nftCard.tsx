import React from 'react';

import { Alignment, Box, Button, Direction, Image, PaddingSize, Spacing, Stack, Text } from '@kibalabs/ui-react';

interface NftCardProps {
  label: string // (top left)
  imageUrl: string // (main image)
  title: string // (main text)
  subtitle: string // (under main text)
  collectionImage?: string // (the "crypto dozer" image)
  collectionTitle?: string
  secondaryButtonTarget?: string // (the view transaction button)
  secondaryButtonText?: string
  primaryButtonTarget?: string // (the view token button)
  primaryButtonText?: string
}

export const NftCard = (props: NftCardProps): React.ReactElement => {
  return (
    <Box variant='card'>
      <Stack direction={Direction.Vertical} paddingBottom={PaddingSize.Wide} shouldAddGutters={true} defaultGutter={PaddingSize.Wide}>
        <Box variant='labelBox'>
          <Text variant={'small'}>{props.label}</Text>
        </Box>
        <Stack direction={Direction.Vertical} defaultGutter={PaddingSize.Default} shouldAddGutters={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center}>
          <Box width='100px' height='100px'>
            <Image isLazyLoadable={true} source={props.imageUrl || props.collectionImage} alternativeText={`${props.title} image`} />
          </Box>
          <Text variant='header5'>{`${props.title || '(unnamed)'}`}</Text>
          <Text variant='subtitle'>{props.subtitle}</Text>
          <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true}>
            {props.collectionImage && (
              <Box width='35px' height='35px'>
                <Image isLazyLoadable={true} source={props.collectionImage} alternativeText={props.collectionTitle} />
              </Box>
            )}
            {props.collectionTitle && <Text variant='small'>{`Part of ${props.collectionTitle}`}</Text>}
          </Stack>
          <Spacing variant={PaddingSize.Narrow} />
          <Stack direction={Direction.Horizontal} defaultGutter={PaddingSize.Default} shouldAddGutters={true} paddingHorizontal={PaddingSize.Default}>
            <Stack.Item growthFactor={1} shrinkFactor={1}>
              {props.secondaryButtonText && props.secondaryButtonTarget && <Button variant='secondary' text={props.secondaryButtonText} target={props.secondaryButtonTarget} />}
            </Stack.Item>
            <Stack.Item growthFactor={1} shrinkFactor={1}>
              {props.primaryButtonText && props.primaryButtonTarget && <Button variant='primary' text={props.primaryButtonText} target={props.primaryButtonTarget} />}
            </Stack.Item>
          </Stack>
        </Stack>
      </Stack>
    </Box>
  );
};

import React from 'react';

import { Alignment, Box, Button, Direction, Image, PaddingSize, Spacing, Stack, Text, Media, TextAlignment, MarkdownText } from '@kibalabs/ui-react';

interface NftCardProps {
  label: string;
  imageUrl: string;
  title: string;
  subtitle: string;
  collectionImage?: string;
  collectionTitle?: string;
  collectionUrl?: string;
  secondaryButtonTarget?: string;
  secondaryButtonText?: string
  primaryButtonTarget?: string;
  primaryButtonText?: string;
  extraLabelVariants?: string[];
  extraLabelBoxVariants?: string[];
}

export const NftCard = (props: NftCardProps): React.ReactElement => {
  const extraLabelVariantsString = props.extraLabelVariants ? `-${props.extraLabelVariants.join('-')}`: '';
  const extraLabelBoxVariantsString = props.extraLabelBoxVariants ? `-${props.extraLabelBoxVariants.join('-')}`: '';
  return (
    <Box variant='card'>
      <Stack direction={Direction.Vertical}>
        <Stack.Item alignment={Alignment.Start} gutterAfter={PaddingSize.Wide}>
          <Box variant={`cardLabelBox${extraLabelBoxVariantsString}`} isFullWidth={false}>
            <Text variant={`cardLabel${extraLabelVariantsString}`}>{props.label}</Text>
          </Box>
        </Stack.Item>
        <Stack direction={Direction.Vertical} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Start}>
          <Stack.Item gutterAfter={PaddingSize.Wide2}>
            <Box width='150px' height='150px'>
              <Media source={props.imageUrl} alternativeText={`${props.title} image`} />
            </Box>
          </Stack.Item>
          <Text variant='header3' alignment={TextAlignment.Center}>{props.title}</Text>
          <Text alignment={TextAlignment.Center}>{props.subtitle}</Text>
          <Spacing variant={PaddingSize.Wide} />
          {props.collectionTitle && (
            <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true}>
              {props.collectionImage && (
                <Box width='25px' height='25px'>
                  <Image source={props.collectionImage} alternativeText={props.collectionTitle} />
                </Box>
              )}
              {props.collectionUrl ? (
                <MarkdownText textVariant='small' source={`Part of [${props.collectionTitle}](${props.collectionUrl})`} />
              ) : (
                <Text variant='small'>{`Part of ${props.collectionTitle}`}</Text>
              )}
            </Stack>
          )}
          <Spacing variant={PaddingSize.Wide2} />
          <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Start} shouldAddGutters={true}>
            {props.secondaryButtonText && props.secondaryButtonTarget && (
              <Stack.Item growthFactor={1} shrinkFactor={1}>
                <Button variant='secondary' text={props.secondaryButtonText} target={props.secondaryButtonTarget} />
              </Stack.Item>
            )}
            {props.primaryButtonText && props.primaryButtonTarget && (
              <Stack.Item growthFactor={1} shrinkFactor={1}>
                <Button variant='primary' text={props.primaryButtonText} target={props.primaryButtonTarget} />
              </Stack.Item>
            )}
          </Stack>
          <Spacing variant={PaddingSize.Wide2} />
        </Stack>
      </Stack>
    </Box>
  );
};

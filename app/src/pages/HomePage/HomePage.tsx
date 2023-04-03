import React from 'react';

import { Alignment, BackgroundView, Box, PrettyText, Text, ContainingView, Direction, Head, Stack, PaddingSize, Image, Spacing, ResponsiveTextAlignmentView, TextAlignment, } from '@kibalabs/ui-react';
import { useGlobals } from '../../globalsContext';
import styled, { keyframes as styledKeyframes} from 'styled-components';

const HeroTextAnimation = styledKeyframes`
  to {
    background-position: 200% 0;
  }
`;

const HeroText = styled.span`
  background: linear-gradient(to right, #a34b4b, #ffffff, #a34b4b);//, #ffffff);
  background-size: 200% auto;
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  animation-name: ${HeroTextAnimation};
  animation-duration: 5s;
  animation-iteration-count: infinite;
`;

export const HomePage = (): React.ReactElement => {
  const { notdClient } = useGlobals();

  return (
    <React.Fragment>
      <Head headId='home'>
        <title>Token Hunt</title>
      </Head>
      <Stack direction={Direction.Vertical} isFullWidth={true} isFullHeight={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Start}>
        <BackgroundView layers={[{imageUrl: 'https://arweave.net/cuGWQb6lme5sVhumf1yrt2GnTuxILG_f-9IhbDyLIEY'}, {color: 'rgba(0, 0, 0, 0.9)'}]}>
          <Box>
            <ContainingView>
              <Stack directionResponsive={{base: Direction.Vertical, medium: Direction.Horizontal}} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Start} paddingVertical={PaddingSize.Wide2} paddingHorizontal={PaddingSize.Wide2}>
                <Stack.Item growthFactor={1} shrinkFactor={1} shouldShrinkBelowContentSize={true}>
                  <ResponsiveTextAlignmentView alignmentResponsive={{base: TextAlignment.Center, medium: TextAlignment.Left}}>
                    <Stack direction={Direction.Vertical} shouldAddGutters={true}>
                      <PrettyText variant='header2-large'>Your explorer for <HeroText>all NFTs and Collections</HeroText> on Ethereum Mainnet 🎭</PrettyText>
                    </Stack>
                  </ResponsiveTextAlignmentView>
                </Stack.Item>
                <Spacing variant={PaddingSize.Wide} />
                <Box widthResponsive={{base: '100%', medium: '40%'}} height='400px' maxHeight='calc(max(400px, 0.5vh))' maxWidth='calc(max(400px, 0.5vh))'>
                  <Stack direction={Direction.Vertical} shouldAddGutters={true}>
                    <Image source='https://arweave.net/cuGWQb6lme5sVhumf1yrt2GnTuxILG_f-9IhbDyLIEY' alternativeText='Title NFT' isFullHeight={true} isFullWidth={true} fitType='cover' />
                    <Text variant='note'>XYZ 123</Text>
                  </Stack>
                </Box>
              </Stack>
            </ContainingView>
          </Box>
        </BackgroundView>
        <ContainingView>
          <Stack direction={Direction.Vertical} isFullWidth={true} childAlignment={Alignment.Start} contentAlignment={Alignment.Center} paddingHorizontal={PaddingSize.Wide2}>
            <Spacing variant={PaddingSize.Wide2} />
            <Text variant='header2'>Trending Collections</Text>
            <Spacing variant={PaddingSize.Wide2} />
          </Stack>
        </ContainingView>
        <Stack.Item growthFactor={1} shrinkFactor={1} />
      </Stack>
    </React.Fragment>
  );
};

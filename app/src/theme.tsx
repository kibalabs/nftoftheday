import { buildTheme, ITheme } from '@kibalabs/ui-react';

export const buildNotdTheme = (): ITheme => {
  const theme = buildTheme({
    colors: {
      brandPrimary: '#6F0000',
      brandSecondary: '#200122',
      background: '#000000',
      text: '#ffffff',
      placeholderText: 'rgba(255, 255, 255, 0.5)',
    },
    fonts: {
      main: {
        url: 'https://fonts.googleapis.com/css?family=Open+Sans:300,400,500,600,700,800,900&display=swap',
      },
    },
    links: {
      default: {
        normal: {
          default: {
            text: {
              color: '$colors.text',
            },
          },
        },
        visited: {
          default: {
            text: {
              color: '$colors.textDarker15',
            },
          },
        },
      },
    },
    texts: {
      default: {
        'font-family': "'Post No Bills Jaffna', sans-serif",
      },
    },
  });
  return theme;
};

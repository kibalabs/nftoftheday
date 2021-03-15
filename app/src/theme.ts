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
          hover: {
            text: {
              color: '$colors.textDark10',
            },
          },
        },
        visited: {
          default: {
            text: {
              color: '$colors.textDark15',
            },
          },
        },
      },
    },
    texts: {
      default: {
        'font-family': "'Post No Bills Jaffna', sans-serif",
      },
      header3: {
        'font-size': '1.5rem',
        'font-weight': '600',
      },
      subtitle: {
        'font-size': '0.75rem',
        'font-weight': '600',
      },
      small: {
        'font-size': '0.85rem',
      },
      light: {
        color: 'rgba(255, 255, 255, 0.75)',
      },
      cardLabel: {
        color: 'rgba(255, 255, 255, 0.75)',
      },
      cardLabelSponsored: {
        color: 'rgba(238, 213, 102, 1)',
      },
      cardLabelRandom: {
        color: 'rgba(46, 180, 255, 1)',
      },
    },
    boxes: {
      card: {
        padding: '0',
        'background-color': 'rgba(255, 255, 255, 0.15)',
        'border-width': '0',
        // 'border-width': '1px',
        // 'border-color': 'rgba(255, 255, 255, 0.5)',
        // 'border-style': 'solid',
        margin: '0',
      },
      cardLabelBox: {
        'border-radius': '0.5em 0 0.2em 0',
        padding: '0.5em 1em',
      },
      cardLabelBoxSponsored: {
        'background-color': 'rgba(238, 213, 102, 0.25)',
      },
      cardLabelBoxRandom: {
        'background-color': 'rgba(46, 180, 255, 0.25)',
      },
    },
    iconButtons: {
      default: {
        disabled: {
          default: {
            background: {
              'background-color': 'rgba(255, 255, 255, 0)',
            },
          },
        },
      },
    },
    buttons: {
      primary: {
        normal: {
          default: {
            background: {
              'background-color': 'rgba(255, 255, 255, 0.25)',
              'border-color': 'rgba(255, 255, 255, 0.3)',
              'border-width': '1px',
            },
            text: {
              color: '$colors.textOnBrand',
            },
          },
          hover: {
            background: {
              'background-color': 'rgba(255, 255, 255, 0.35)',
            },
          },
          press: {
            background: {
              'background-color': 'rgba(255, 255, 255, 0.55)',
            },
          },
          focus: {
            background: {
              'border-color': 'rgba(255, 255, 255, 0.75)',
            },
          },
        },
      },
      secondary: {
        normal: {
          default: {
            background: {
              'border-color': 'rgba(255, 255, 255, 0.3)',
              'border-width': '1px',
            },
            text: {
              color: '$colors.textOnBrand',
            },
          },
          hover: {
            background: {
              'background-color': 'rgba(255, 255, 255, 0.35)',
            },
          },
          press: {
            background: {
              'background-color': 'rgba(255, 255, 255, 0.55)',
            },
          },
          focus: {
            background: {
              'border-color': 'rgba(255, 255, 255, 0.75)',
            },
          },
        },
      },
      tertiary: {
        normal: {
          default: {
            background: {
              'border-width': '0',
            },
            text: {
              color: '$colors.textOnBrand',
            },
          },
          hover: {
            background: {
              'background-color': 'rgba(255, 255, 255, 0.35)',
            },
          },
          press: {
            background: {
              'background-color': 'rgba(255, 255, 255, 0.55)',
            },
          },
          focus: {
            background: {
              'border-color': 'rgba(255, 255, 255, 0.75)',
            },
          },
        },
      },
    },
  });
  return theme;
};

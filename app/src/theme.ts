import { buildTheme, ITheme } from '@kibalabs/ui-react';

const defaultTheme = buildTheme();
export const buildNotdTheme = (): ITheme => {
  const theme = buildTheme({
    dimensions: {
      fontSize: '18px',
    },
    fonts: {
      main: {
        url: 'https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@300;400;700&display=swap',
      },
    },
    colors: {
      brandPrimary: '#6F0000',
      brandSecondary: '#200122',
      background: '#000000',
      text: '#ffffff',
      placeholderText: 'rgba(255, 255, 255, 0.5)',
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
        'font-family': "'Roboto Condensed', sans-serif",
        'font-weight': '400',
      },
      header3: {
        'font-size': '1.5rem',
        'font-weight': '600',
        'margin-bottom': '0.25em',
      },
      header4: {
        'font-size': '1.3rem',
        'font-weight': '600',
      },
      subtitle: {
        'font-size': '0.75rem',
        'font-weight': '600',
      },
      small: {
        'font-size': '0.85rem',
        'line-height': '1em',
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
      // NOTE(krishan711): this is a hack, update the library to add a 'shouldClipContent' param or similar
      singleLine: {
        'max-width': '100%',
        overflow: 'hidden',
        'text-overflow': 'ellipsis',
      },
    },
    boxes: {
      phBanner: {
        padding: `${defaultTheme.dimensions.paddingWide} ${defaultTheme.dimensions.paddingWide}`,
        'background-color': 'rgba(0, 0, 0, 0.5)',
      },
      card: {
        padding: '0',
        'background-color': 'rgba(255, 255, 255, 0.15)',
        'border-width': '0',
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
      unrounded: {
        'border-radius': '0',
      },
      avatar: {
        'border-color': '$colors.brandSecondary',
        'background-color': '$colors.brandSecondary',
        'border-width': '5px',
      },
      divider: {
        'background-color': 'rgba(255, 255, 255, 0.15)',
      },
      metricCard: {
        padding: '0',
        'background-color': 'rgba(255, 255, 255, 0.15)',
        'border-width': '0',
        margin: '0',
      },
      tokenCard: {
        padding: '0px',
        'background-color': 'rgba(255, 255, 255, 0.15)',
        'border-width': '0',
        'border-radius': '10px',
      },
      tokenSaleRow: {
        padding: '0',
        'background-color': 'rgba(255, 255, 255, 0.15)',
        'border-width': '0',
        margin: '0',
        'border-radius': '0',
      },
    },
    images: {
      default: {
        background: {
          'border-radius': '0',
        },
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
      default: {
        normal: {
          default: {
            text: {
              'font-size': '0.8em',
            },
          },
        },
      },
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
      small: {
        normal: {
          default: {
            background: {
              'border-width': '0',
            },
            text: {
              color: '$colors.textOnBrand',
              'font-size': '1em',
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
    dialogs: {
      default: {
        backdropColor: 'rgba(0, 0, 0, 0.7)',
        background: {
          'background-color': '$colors.brandPrimaryDark10',
        },
      },
    },
    inputWrappers: {
      dialogInput: {
        normal: {
          default: {
            background: {
              'background-color': 'rgba(255, 255, 255, 0.25)',
            },
          },
        },
      },
    },
  });
  return theme;
};

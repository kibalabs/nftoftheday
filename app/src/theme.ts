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
      brandPrimary: '#00A3FF',
      brandSecondary: '#7500E5',
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
      // NOTE(krishan711): this is a hack, update the library to add a 'shouldClipContent' param or similar
      forcedMultipleLine: {
        'word-break': 'break-word',
      },
    },
    prettyTexts: {
      header2: {
        normal: {
          default: {
            text: {
              'font-size': '3em',
            },
          },
          strong: {
            text: {
              color: '$colors.brandPrimaryLight50',
              'font-weight': 'bold',
            },
          },
        },
      },
    },
    boxes: {
      phBanner: {
        padding: `${defaultTheme.dimensions.paddingWide} ${defaultTheme.dimensions.paddingWide}`,
        'background-color': 'rgba(0, 0, 0, 0.5)',
      },
      card: {
        padding: '0',
        'background-color': 'rgba(0, 0, 0, 0.45)',
        'border-width': '0',
        margin: '0',
      },
      tooltip: {
        'background-color': '$colors.background',
      },
      unrounded: {
        'border-radius': '0',
      },
      avatar: {
        'border-color': '$colors.background',
        'background-color': '$colors.background',
        'border-width': '5px',
      },
      divider: {
        'background-color': 'rgba(0, 0, 0, 0.5)',
      },
      metricCard: {
        padding: '0',
        'background-color': 'rgba(0, 0, 0, 0.5)',
        'border-width': '0',
        margin: '0',
      },
      tokenCard: {
        padding: '0px',
        'background-color': 'rgba(0, 0, 0, 0.5)',
        'border-width': '0',
        'border-radius': '10px',
      },
      tokenSaleRow: {
        padding: '0',
        'background-color': '$colors.backgroundLight10',
        'border-width': '0',
        margin: '0',
        // 'border-radius': '0',
      },
    },
    images: {
      default: {
        background: {
          'border-radius': '0',
        },
      },
      rounded: {
        background: {
          'border-radius': defaultTheme.dimensions.borderRadius,
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
    linkBases: {
      default: {
        normal: {
          default: {
            background: {
              'background-color': 'rgba(0, 0, 0, 0)',
            },
          },
          hover: {
            background: {
              'background-color': 'rgba(255, 255, 255, 0.15)',
            },
          },
        },
      },
    },
    listItems: {
      default: {
        normal: {
          default: {
            background: {
              'background-color': 'rgba(0, 0, 0, 0.95)',
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
      default: {
        normal: {
          default: {
            background: {
              'background-color': 'rgba(0, 0, 0, 0.25)',
            },
          },
        },
      },
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
    selectableViews: {
      default: {
        normal: {
          default: {
            background: {
              'border-width': '0',
              padding: '0',
            },
          },
        },
      },
    },
    collapsibleBoxes: {
      default: {
        normal: {
          default: {
            background: {
              'border-color': '$colors.backgroundLight10',
              'border-width': '1px',
            },
            headerBackground: {
              'background-color': '$colors.backgroundLight10',
            },
          },
        },
      },
    },
    titledCollapsibleBoxes: {
      default: {
        normal: {
          default: {
            background: {
              'border-color': '$colors.backgroundLight10',
              'border-width': '1px',
            },
            headerBackground: {
              'background-color': '$colors.backgroundLight10',
            },
          },
        },
      },
    },
  });
  return theme;
};

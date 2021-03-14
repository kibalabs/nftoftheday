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
    buttons: {
      primary: {
        normal: {
          default: {
            background: {
              'background-color': 'rgba(255,255,255,0.25)',
              'border-color': 'rgba(255,255,255,0.5)',
            },
            text: {
              color: '$colors.textOnBrand',
            },
          },
          hover: {
            background: {
              'background-color': 'rgba(255,255,255,0.35)',
            },
          },
          press: {
            background: {
              'background-color': 'rgba(255,255,255,0.75)',
            },
          },
        },
      },
      secondary: {
        normal: {
          default: {
            background: {
              'border-color': 'rgba(255, 255, 255, 0.5)',
              // 'background-color': 'rgba(255, 255, 255, 0.05)',
              // 'border-color': 'rgba(255, 255, 255, 0.1)',
              // 'border-width': '1px',
            },
            text: {
              color: '$colors.textOnBrand',
            },
          },
          hover: {
            background: {
              'background-color': 'rgba(255,255,255,0.35)',
            },
          },
          press: {
            background: {
              'background-color': 'rgba(255, 255, 255, 0.45)',
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
    },
    boxes: {
      // card: {
      //   'background-color': 'rgba(255, 255, 255, 0.15)',
      //   'border-color': 'rgba(255, 255, 255, 0.5)',
      //   margin: '0',
      // },
      card: {
        padding: 'none',
        'background-color': 'rgba(255, 255, 255, 0.15)',
        'border-width': '1px',
        'border-color': 'rgba(46, 180, 255, 0.5)',
        'border-style': 'solid',
      },
      labelBox: {
        'border-radius': '0.5rem 0 0 0',
        padding: '0.5rem 0 0 0.75rem',
      },
    },
    // buttons: {
    //   primary: {
    //     normal: {
    //       default: {
    //         background: {
    //           'background-color': 'rgba(255, 255, 255, 0.25)',
    //           'border-color': 'rgba(255, 255, 255, 0.5)',
    //           'border-width': '1px',
    //         },
    //         text: {
    //           color: 'white',
    //         },
    //       },
    //       hover: {
    //         background: {
    //           'background-color': 'rgba(255, 255, 255, 0.35)',
    //         },
    //       },
    //       press: {
    //         background: {
    //           'background-color': 'rgba(255, 255, 255, 0.45)',
    //         },
    //       },
    //       focus: {
    //         background: {
    //           'border-color': 'rgba(255, 255, 255, 0.75)',
    //         },
    //       },
    //     },
    //   },
    // },
  });
  return theme;
};

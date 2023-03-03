/* eslint-disable */
import { Tag, MetaTag } from '@kibalabs/build/scripts/plugins/injectSeoPlugin.js';

const title = 'Token Hunt';
const description = 'Your daily dose of the best NFTs';
const url = 'https://nft.tokenhunt.io'
const imageUrl = `${url}/assets/banner.png`;

const seoTags = [
  new MetaTag('description', description),
  new Tag('meta', {property: 'og:title', content: title}),
  new Tag('meta', {property: 'og:description', content: description}),
  new Tag('meta', {property: 'og:image', content: imageUrl}),
  new Tag('meta', {property: 'og:url', content: url}),
  new MetaTag('twitter:card', 'summary_large_image'),
  // new MetaTag('twitter:site', '@mdtp_app'),
  new Tag('link', {rel: 'canonical', href: url}),
  new Tag('link', {rel: 'icon', type: 'image/png', href: '/assets/icon.png'}),
];

export default (config) => {
  config.seoTags = seoTags;
  config.title = title;
  config.pages = [{
    path: '/',
    filename: 'index.html',
  }];
  return config;
};

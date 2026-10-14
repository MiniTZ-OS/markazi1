import next from 'eslint-config-next';

export default [
  {
    files: ['**/*.{js,ts,jsx,tsx}'],
    rules: {
      ...next.rules,
    },
  },
];

// CRA ships a default "renders learn react link" test that doesn't apply here.
// Replace it with a simple store-initialization smoke test that has no
// react-router-dom dependency (RRD v7 ships ESM, which Jest can't transform
// without extra config that CRA's preset doesn't include).
import store from './store/store';

test('redux store initializes with defined state', () => {
  expect(store).toBeDefined();
  const state = store.getState();
  expect(state).toBeDefined();
  expect(typeof state).toBe('object');
});

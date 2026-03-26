import { getWarnCount } from '@/api/camera/warn.js'
// import createPersistedState from 'vuex-persistedstate';

const state = {
  alertCount: null
}

const mutations = {
  SET_ALERT_COUNT(state, count) {
    state.alertCount = count
  }
}

const actions = {
  async fetchAlertCount({ state, commit }) {
    if (state.alertCount !== null) {
      return;
    }

    try {
      const response = await getWarnCount();
      const count = response.data;
      commit('SET_ALERT_COUNT', count);
    } catch (error) {
      console.error('Failed to fetch alert count:', error);
    }
  }
}

export default {
  state,
  mutations,
  actions,
  // plugins: [createPersistedState()]
}

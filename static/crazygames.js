/* CrazyGames Basic Launch adapter. Loaded only when the game is embedded on CrazyGames. */
(async function initCrazyGamesAdapter() {
  document.documentElement.dataset.mipoAdapter = JSON.stringify({create: typeof window.createGame, instant: new URLSearchParams(location.search).get('instantJoin')});
  const isCrazyGamesOrigin = (value) => {
    try { return /(^|\.)crazygames\.com$/i.test(new URL(value).hostname); }
    catch (_) { return false; }
  };
  const embeddedOnCrazyGames =
    isCrazyGamesOrigin(document.referrer) ||
    (window.location.hostname && /(^|\.)crazygames\.com$/i.test(window.location.hostname)) ||
    (window.location.ancestorOrigins && Array.from(window.location.ancestorOrigins).some(isCrazyGamesOrigin));
  document.documentElement.dataset.mipoEmbedded = String(embeddedOnCrazyGames);
  if (!embeddedOnCrazyGames) return;

  const loadSdk = () => new Promise((resolve, reject) => {
    if (window.CrazyGames && window.CrazyGames.SDK) return resolve();
    const script = document.createElement('script');
    script.src = 'https://sdk.crazygames.com/crazygames-sdk-v3.js';
    script.async = true;
    script.onload = resolve;
    script.onerror = () => reject(new Error('CrazyGames SDK failed to load'));
    document.head.appendChild(script);
  });

  let launchHandled = false;
  const pageParams = new URLSearchParams(window.location.search);
  // An optional platform SDK must not hold up the iframe's playable launch.
  if (pageParams.get('instantJoin') === 'true' && !pageParams.get('code') && typeof window.createGame === 'function') {
    try {
      if (typeof window.mode === 'function') window.mode('create');
      const continueButton = document.getElementById('hostIntroContinue');
      if (continueButton) continueButton.click();
      const hostName = document.getElementById('cname');
      if (hostName && !hostName.value.trim()) hostName.value = 'Player';
      await window.createGame();
      launchHandled = !document.getElementById('game')?.classList.contains('hidden');
    } catch (error) {
      console.warn('MIPO instant launch can be completed with Create game.', error);
    }
  }

  try {
    await loadSdk();
    await window.CrazyGames.SDK.init();
    const cg = window.CrazyGames.SDK.game || {};

    let gameplayActive = false;
    let lastRoomSignature = '';
    const call = (name, ...args) => {
      try { if (typeof cg[name] === 'function') return cg[name](...args); } catch (_) {}
    };
    const startGameplay = () => {
      if (gameplayActive) return;
      gameplayActive = true;
      call('gameplayStart');
    };
    const stopGameplay = () => {
      if (!gameplayActive) return;
      gameplayActive = false;
      call('gameplayStop');
    };
    function syncRoom(state) {
      if (!state || !state.code) return;
      if (state.status === 'finished') {
        call('leftRoom');
        lastRoomSignature = '';
        stopGameplay();
        return;
      }
      const isJoinable = state.status === 'lobby';
      const room = {
        roomId: String(state.code),
        isJoinable,
        inviteParams: { code: String(state.code) }
      };
      const signature = JSON.stringify(room);
      if (signature !== lastRoomSignature) {
        call('updateRoom', room);
        lastRoomSignature = signature;
      }
      startGameplay();
    }

    // Notify CrazyGames when a room is created/joined and as room state changes.
    if (typeof window.req === 'function') {
      const originalReq = window.req;
      window.req = async function(path, body) {
        const result = await originalReq(path, body);
        if ((path === '/api/create' || path === '/api/join') && result && result.code) {
          call('updateRoom', {
            roomId: String(result.code),
            isJoinable: true,
            inviteParams: { code: String(result.code) }
          });
          lastRoomSignature = '';
          startGameplay();
        } else if (typeof path === 'string' && path.startsWith('/api/state/') && result) {
          syncRoom(result);
        }
        return result;
      };
      try { req = window.req; } catch (_) {}
    }

    async function joinFromInvite(params) {
      const invite = params && (params.inviteParams || params);
      const code = invite && (invite.code || invite.roomCode || invite.roomId);
      if (!code || typeof window.joinGame !== 'function') return;
      const codeInput = document.getElementById('jcode');
      const nameInput = document.getElementById('jname');
      if (!codeInput || !nameInput) return;
      if (typeof window.mode === 'function') window.mode('join');
      codeInput.value = String(code).toUpperCase().slice(0, 5);
      if (!nameInput.value.trim()) nameInput.value = 'Guest ' + Math.random().toString(36).slice(2, 6).toUpperCase();
      await window.joinGame();
    }

    if (typeof cg.addJoinRoomListener === 'function') {
      cg.addJoinRoomListener(joinFromInvite);
    }
    const launchParams = new URLSearchParams(window.location.search);
    const instantMultiplayer = cg.isInstantMultiplayer || launchParams.get('instantJoin') === 'true';
    if (launchParams.get('qaTool') === 'true') console.info('MIPO SDK launch ' + JSON.stringify({ environment: window.CrazyGames.SDK.environment, instantMultiplayer, sdkInstant: cg.isInstantMultiplayer, create: typeof window.createGame, join: typeof window.joinGame }));
    const initialInvite = cg.inviteParams || {};
    const initialCode = initialInvite.code || initialInvite.roomCode || initialInvite.roomId;
    if (initialCode && !launchHandled) {
      await joinFromInvite(initialInvite);
    } else if (!launchHandled && instantMultiplayer && typeof window.createGame === 'function') {
      if (typeof window.mode === 'function') window.mode('create');
      const introContinue = document.getElementById('hostIntroContinue');
      if (introContinue) introContinue.click();
      const nameInput = document.getElementById('cname');
      if (nameInput && !nameInput.value.trim()) nameInput.value = 'Player';
      await window.createGame();
    }

    // Use the CrazyGames invite URL when players tap MIPO's existing share control.
    if (typeof window.share === 'function' && typeof cg.inviteLink === 'function') {
      const originalShare = window.share;
      window.share = async function() {
        try {
          const state = window.lastState;
          const code = state && state.code;
          if (!code) return originalShare();
          const url = await cg.inviteLink({ code: String(code) });
          if (!url) return originalShare();
          if (navigator.share) {
            await navigator.share({ title: 'Play MIPO', text: 'Join my MIPO game', url });
          } else if (navigator.clipboard) {
            await navigator.clipboard.writeText(url);
            if (typeof window.toast === 'function') window.toast('Invite link copied');
          }
        } catch (_) { return originalShare(); }
      };
    }
  } catch (error) {
    console.warn('CrazyGames integration unavailable; standard MIPO play remains enabled.', error);
  }
})();

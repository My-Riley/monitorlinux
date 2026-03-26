// /**
//  * @constructor
//  * @param {string} videoElement -  dom ID
//  * @param {string} srvurl -  WebRTC 流媒体服务器的 URL（默认为当前页面地址）
//  */
class WebRtcStreamer {
  constructor(videoElement, srvurl) {
    if (typeof videoElement === "string") {
      this.videoElement = document.getElementById(videoElement);
    } else {
      this.videoElement = videoElement;
    }
    this.srvurl =
      srvurl ||
      `${location.protocol}//${window.location.hostname}:${window.location.port}`;
    this.pc = null; // PeerConnection 实例

    // 媒体约束条件
    this.mediaConstraints = {
      offerToReceiveAudio: true,
      offerToReceiveVideo: true,
    };

    this.iceServers = null; // ICE 服务器配置
    this.earlyCandidates = []; // 提前收集的候选者
  }

  // /**
  //  * HTTP 错误处理器
  //  * @param {Response} response - HTTP 响应
  //  * @throws {Error} 当响应不成功时抛出错误
  //  */
  _handleHttpErrors(response) {
    if (!response.ok) {
      throw Error(response.statusText);
    }
    return response;
  }

  // /**
  //  * 连接 WebRTC 视频流到指定的 videoElement
  //  * @param {string} videourl - 视频流 URL
  //  * @param {string} audiourl - 音频流 URL
  //  * @param {string} options - WebRTC 通话的选项
  //  * @param {MediaStream} localstream - 本地流
  //  * @param {string} prefmime - 优先的 MIME 类型
  //  */
  connect(videourl, audiourl, options, localstream, prefmime) {
    this.disconnect();

    if (!this.iceServers) {
      fetch(`${this.srvurl}/api/getIceServers`)
        .then(this._handleHttpErrors)
        .then((response) => response.json())
        .then((response) =>
          this.onReceiveGetIceServers(
            response,
            videourl,
            audiourl,
            options,
            localstream,
            prefmime
          )
        )
        .catch((error) => this.onError(`获取 ICE 服务器错误: ${error}`));
    } else {
      this.onReceiveGetIceServers(
        this.iceServers,
        videourl,
        audiourl,
        options,
        localstream,
        prefmime
      );
    }
  }

  // /**
  //  * 断开 WebRTC 视频流，并清空 videoElement 的视频源
  //  */
  disconnect() {
    if (this.videoElement?.srcObject) {
      this.videoElement.srcObject.getTracks().forEach((track) => {
        track.stop();
        this.videoElement.srcObject.removeTrack(track);
      });
    }
    if (this.pc) {
      fetch(`${this.srvurl}/api/hangup?peerid=${this.pc.peerid}`)
        .then(this._handleHttpErrors)
        .catch((error) => this.onError(`hangup ${error}`));

      try {
        this.pc.close();
      } catch (e) {
      }
      this.pc = null;
    }
  }

  // /**
  //  * 获取 ICE 服务器配置的回调
  //  * @param {Object} iceServers - ICE 服务器配置
  //  * @param {string} videourl - 视频流 URL
  //  * @param {string} audiourl - 音频流 URL
  //  * @param {string} options - WebRTC 通话的选项
  //  * @param {MediaStream} stream - 本地流
  //  * @param {string} prefmime - 优先的 MIME 类型
  //  */
  onReceiveGetIceServers(
    iceServers,
    videourl,
    audiourl,
    options,
    stream,
    prefmime
  ) {
    this.iceServers = iceServers;
    this.pcConfig = iceServers || { iceServers: [] };
    try {
      this.createPeerConnection();

      let callurl = `${this.srvurl}/api/call?peerid=${this.pc.peerid
        }&url=${encodeURIComponent(videourl)}`;
      if (audiourl) {
        callurl += `&audiourl=${encodeURIComponent(audiourl)}`;
      }
      if (options) {
        callurl += `&options=${encodeURIComponent(options)}`;
      }

      if (stream) {
        this.pc.addStream(stream);
      }

      this.earlyCandidates.length = 0;

      this.pc
        .createOffer(this.mediaConstraints)
        .then((sessionDescription) => {
          // console.log(`创建 Offer: ${JSON.stringify(sessionDescription)}`);

          if (prefmime !== undefined) {
            const [prefkind] = prefmime.split("/");
            const codecs = RTCRtpReceiver.getCapabilities(prefkind).codecs;
            const preferredCodecs = codecs.filter(
              (codec) => codec.mimeType === prefmime
            );

            this.pc
              .getTransceivers()
              .filter(
                (transceiver) => transceiver.receiver.track.kind === prefkind
              )
              .forEach((tcvr) => {
                if (tcvr.setCodecPreferences) {
                  tcvr.setCodecPreferences(preferredCodecs);
                }
              });
          }

          this.pc
            .setLocalDescription(sessionDescription)
            .then(() => {
              fetch(callurl, {
                method: "POST",
                body: JSON.stringify(sessionDescription),
              })
                .then(this._handleHttpErrors)
                .then((response) => response.json())
                .then((response) => this.onReceiveCall(response))
                .catch((error) => this.onError(`调用错误: ${error}`));
            })
            .catch((error) =>
            );
        })
        .catch((error) =>
        );
    } catch (e) {
      this.disconnect();
      alert(`连接错误: ${e}`);
    }
  }

  /**
   * 创建 PeerConnection 实例
   */

  createPeerConnection() {
    this.pc = new RTCPeerConnection(this.pcConfig);
    this.pc.peerid = Math.random(); // 生成唯一的 peerid

    // 监听 ICE 候选者事件
    this.pc.onicecandidate = (evt) => this.onIceCandidate(evt);
    this.pc.onaddstream = (evt) => this.onAddStream(evt);
    this.pc.oniceconnectionstatechange = () => {
      if (this.videoElement) {
        if (this.pc.iceConnectionState === "connected") {
          this.videoElement.style.opacity = "1.0";
        } else if (this.pc.iceConnectionState === "disconnected") {
          this.videoElement.style.opacity = "0.25";
        } else if (["failed", "closed"].includes(this.pc.iceConnectionState)) {
          this.videoElement.style.opacity = "0.5";
        } else if (this.pc.iceConnectionState === "new") {
          this.getIceCandidate();
        }
      }
    };
    return this.pc;
  }

  onAddStream(event) {
    this.videoElement.srcObject = event.stream;
    const promise = this.videoElement.play();
    if (promise !== undefined) {
      promise.catch((error) => {
        console.warn(`error: ${error}`);
        this.videoElement.setAttribute("controls", true);
      });
    }
  }

  onIceCandidate(event) {
    if (event.candidate) {
      if (this.pc.currentRemoteDescription) {
        this.addIceCandidate(this.pc.peerid, event.candidate);
      } else {
        this.earlyCandidates.push(event.candidate);
      }
    } else {
    }
  }

  /**
   * 添加 ICE 候选者到 PeerConnection
   * @param {RTCIceCandidate} candidate - ICE 候选者
   */
  addIceCandidate(peerid, candidate) {
    fetch(`${this.srvurl}/api/addIceCandidate?peerid=${peerid}`, {
      method: "POST",
      body: JSON.stringify(candidate),
    })
      .then(this._handleHttpErrors)
      .catch((error) => this.onError(`addIceCandidate ${error}`));
  }

  /**
   * 处理 WebRTC 通话的响应
   * @param {Object} message - 来自服务器的响应消息
   */
  onReceiveCall(dataJson) {
    const descr = new RTCSessionDescription(dataJson);
    this.pc
      .setRemoteDescription(descr)
      .then(() => {
        while (this.earlyCandidates.length) {
          const candidate = this.earlyCandidates.shift();
          this.addIceCandidate(this.pc.peerid, candidate);
        }
        this.getIceCandidate();
      })
      .catch((error) =>
      );
  }

  getIceCandidate() {
    fetch(`${this.srvurl}/api/getIceCandidate?peerid=${this.pc.peerid}`)
      .then(this._handleHttpErrors)
      .then((response) => response.json())
      .then((response) => this.onReceiveCandidate(response))
      .catch((error) => this.onError(`getIceCandidate ${error}`));
  }

  onReceiveCandidate(dataJson) {
    if (dataJson) {
      dataJson.forEach((candidateData) => {
        const candidate = new RTCIceCandidate(candidateData);
        this.pc
          .addIceCandidate(candidate)
          .catch((error) =>
          );
      });
    }
  }

  /**
   * 错误处理器
   * @param {string} message - 错误信息
   */
  onError(status) {
    console.error(`WebRTC 错误: ${status}`);
  }
}

export default WebRtcStreamer;

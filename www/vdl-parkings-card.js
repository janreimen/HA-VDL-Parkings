
/**
 * VDL Parkings Lovelace Card
 *
 * Automatically discovers parking entities provided by
 * the VDL Parkings Home Assistant integration.
 *
 * Version: 0.1.4
 * Repository: https://github.com/janreimen/HA-VDL-Parkings
 */

class VdlParkingsCard extends HTMLElement {
  constructor() {
    super();

    this.attachShadow({ mode: "open" });
    this._config = {};
    this._hass = null;
  }

  setConfig(config) {
    if (!config || typeof config !== "object") {
      throw new Error("Invalid VDL Parkings card configuration.");
    }

    this._config = {
      title: "VDL Parkings",
      show_status: true,
      show_occupancy: true,
      parking_ids: [],
      ...config,
    };

    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  get hass() {
    return this._hass;
  }

  getCardSize() {
    return 3;
  }

  static getConfigElement() {
    return document.createElement("vdl-parkings-card-editor");
  }

  static getStubConfig() {
    return {
      title: "VDL Parkings",
      show_status: true,
      show_occupancy: true,
    };
  }

  _getParkingId(state) {
    return state?.attributes?.parking_id !== undefined
      ? String(state.attributes.parking_id)
      : null;
  }

  _getParkingName(state) {
    return (
      state?.attributes?.parking_name ||
      state?.attributes?.friendly_name ||
      state?.entity_id ||
      "Parking"
    );
  }

  _findParkingEntity(parkingId, suffix) {
    if (!this._hass) return null;

    return Object.values(this._hass.states).find((state) => {
      return (
        this._getParkingId(state) === parkingId &&
        state.entity_id.endsWith(`_${suffix}`)
      );
    }) || null;
  }

  _findBinarySensor(parkingId, key) {
    if (!this._hass) return null;

    return Object.values(this._hass.states).find((state) => {
      return (
        state.entity_id.startsWith("binary_sensor.") &&
        this._getParkingId(state) === parkingId &&
        state.entity_id.endsWith(`_${key}`)
      );
    }) || null;
  }

  _discoverParkings() {
    if (!this._hass) return [];

    const configuredIds = Array.isArray(this._config.parking_ids)
      ? this._config.parking_ids.map(String)
      : [];

    const availableSensors = Object.values(this._hass.states).filter(
      (state) =>
        state.entity_id.startsWith("sensor.") &&
        state.entity_id.endsWith("_available_spaces") &&
        this._getParkingId(state) !== null
    );

    return availableSensors
      .map((available) => {
        const parkingId = this._getParkingId(available);

        return {
          id: parkingId,
          name: this._getParkingName(available),
          available,
          capacity: this._findParkingEntity(parkingId, "total_capacity"),
          occupied: this._findParkingEntity(parkingId, "occupied_spaces"),
          occupancy: this._findParkingEntity(parkingId, "occupancy_rate"),
          open: this._findBinarySensor(parkingId, "open"),
          full: this._findBinarySensor(parkingId, "full"),
          outOfService: this._findBinarySensor(
            parkingId,
            "out_of_service"
          ),
        };
      })
      .filter(
        (parking) =>
          configuredIds.length === 0 || configuredIds.includes(parking.id)
      )
      .sort((a, b) => a.name.localeCompare(b.name));
  }

  _formatValue(state, fallback = "—") {
    if (!state || state.state === "unknown" || state.state === "unavailable") {
      return fallback;
    }

    return state.state;
  }

  _isOn(state) {
    return state && state.state === "on";
  }

  _createElement(tag, className, text) {
    const element = document.createElement(tag);

    if (className) {
      element.className = className;
    }

    if (text !== undefined && text !== null) {
      element.textContent = String(text);
    }

    return element;
  }

  _createStatus(label, active, activeClass = "active") {
    const status = this._createElement(
      "span",
      `status ${active ? activeClass : "inactive"}`,
      label
    );

    return status;
  }

  _renderParking(parking) {
    const card = this._createElement("article", "parking");

    const heading = this._createElement(
      "div",
      "parking-heading"
    );

    heading.appendChild(
      this._createElement("h3", "parking-name", parking.name)
    );

    const availableValue = this._formatValue(parking.available);

    heading.appendChild(
      this._createElement(
        "span",
        "available-value",
        `${availableValue} free`
      )
    );

    card.appendChild(heading);

    const details = this._createElement("div", "details");

    details.appendChild(
      this._createElement(
        "span",
        "detail",
        `Capacity: ${this._formatValue(parking.capacity)}`
      )
    );

    details.appendChild(
      this._createElement(
        "span",
        "detail",
        `Occupied: ${this._formatValue(parking.occupied)}`
      )
    );

    card.appendChild(details);

    if (this._config.show_occupancy) {
      const rawRate = Number(parking.occupancy?.state);
      const rate = Number.isFinite(rawRate)
        ? Math.min(100, Math.max(0, rawRate))
        : null;

      const occupancy = this._createElement("div", "occupancy");

      const occupancyHeader = this._createElement(
        "div",
        "occupancy-header"
      );

      occupancyHeader.appendChild(
        this._createElement("span", "", "Occupancy")
      );

      occupancyHeader.appendChild(
        this._createElement(
          "strong",
          "",
          rate === null ? "—" : `${rate.toFixed(1)}%`
        )
      );

      occupancy.appendChild(occupancyHeader);

      const bar = this._createElement("div", "bar");
      const fill = this._createElement("div", "bar-fill");

      if (rate !== null) {
        fill.style.width = `${rate}%`;
      }

      bar.appendChild(fill);
      occupancy.appendChild(bar);
      card.appendChild(occupancy);
    }

    if (this._config.show_status) {
      const statuses = this._createElement("div", "statuses");

      if (parking.open) {
        statuses.appendChild(
          this._createStatus("Open", this._isOn(parking.open), "success")
        );
      }

      if (parking.full) {
        statuses.appendChild(
          this._createStatus("Full", this._isOn(parking.full), "warning")
        );
      }

      if (parking.outOfService) {
        statuses.appendChild(
          this._createStatus(
            "Out of service",
            this._isOn(parking.outOfService),
            "danger"
          )
        );
      }

      card.appendChild(statuses);
    }

    return card;
  }

  _render() {
    if (!this.shadowRoot || !this._config) return;

    const style = this._createElement("style");

    style.textContent = `
      :host {
        display: block;
      }

      ha-card {
        padding: 16px;
        overflow: hidden;
      }

      .title {
        margin: 0 0 16px;
        font-size: 1.25rem;
        font-weight: 600;
      }

      .parking-list {
        display: grid;
        grid-template-columns: repeat(
          auto-fit,
          minmax(min(100%, 240px), 1fr)
        );
        gap: 12px;
      }

      .parking {
        padding: 14px;
        border: 1px solid var(--divider-color);
        border-radius: 10px;
        background: var(--ha-card-background, var(--card-background-color));
      }

      .parking-heading {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 12px;
      }

      .parking-name {
        margin: 0;
        font-size: 1.05rem;
        font-weight: 600;
      }

      .available-value {
        white-space: nowrap;
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--success-color);
      }

      .details {
        display: flex;
        flex-wrap: wrap;
        gap: 6px 14px;
        margin-top: 12px;
        color: var(--secondary-text-color);
        font-size: 0.9rem;
      }

      .occupancy {
        margin-top: 14px;
      }

      .occupancy-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 6px;
        font-size: 0.85rem;
      }

      .bar {
        height: 8px;
        overflow: hidden;
        border-radius: 8px;
        background: var(--divider-color);
      }

      .bar-fill {
        height: 100%;
        border-radius: inherit;
        background: var(--info-color);
        transition: width 0.3s ease;
      }

      .statuses {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 14px;
      }

      .status {
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 600;
      }

      .status.inactive {
        background: var(--secondary-background-color);
        color: var(--secondary-text-color);
      }

      .status.success {
        background: var(--success-color);
        color: white;
      }

      .status.warning {
        background: var(--warning-color);
        color: var(--primary-text-color);
      }

      .status.danger {
        background: var(--error-color);
        color: white;
      }

      .empty {
        padding: 12px 0;
        color: var(--secondary-text-color);
      }
    `;

    const haCard = this._createElement("ha-card");
    const title = this._createElement(
      "h2",
      "title",
      this._config.title
    );

    haCard.appendChild(title);

    if (!this._hass) {
      haCard.appendChild(
        this._createElement("p", "empty", "Waiting for Home Assistant…")
      );
    } else {
      const parkings = this._discoverParkings();

      if (parkings.length === 0) {
        haCard.appendChild(
          this._createElement(
            "p",
            "empty",
            "No VDL parking entities found. Check the integration and entity availability."
          )
        );
      } else {
        const list = this._createElement("div", "parking-list");

        parkings.forEach((parking) => {
          list.appendChild(this._renderParking(parking));
        });

        haCard.appendChild(list);
      }
    }

    this.shadowRoot.replaceChildren(style, haCard);
  }
}

customElements.define("vdl-parkings-card", VdlParkingsCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "vdl-parkings-card",
  name: "VDL Parkings Card",
  description: "Displays live availability and occupancy of VDL car parks.",
  preview: true,
});


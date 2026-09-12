"""View modul API References."""

from __future__ import annotations

import sqlite3
from typing import Any

import flet as ft

from src.app.components.cards import (
    action_button,
    build_label_checkboxes,
    copy_button,
    get_selected_label_ids,
    render_label_chips,
)
from src.app.theme import PALETTE
from src.app.utils.clipboard import copy_to_clipboard
from src.app.views.base import BaseView
from src.core.models import ApiRef
from src.core.secrets import get_secret, store_secret
from src.core.storage import api_refs_repo, labels_repo


class ApiRefsView(BaseView):
    """View untuk CRUD API reference."""

    def __init__(self, page: ft.Page, conn: sqlite3.Connection) -> None:
        super().__init__(
            page, "API References", ft.Icons.CODE_OUTLINED, self._open_add
        )
        self.conn = conn
        self.refresh()

    def _open_add(self) -> None:
        self._open_dialog(None)

    def _open_edit(self, ref: ApiRef) -> None:
        self._open_dialog(ref)

    def _duplicate(self, ref: ApiRef) -> None:
        api_refs_repo.create_api_ref(
            self.conn,
            ApiRef(
                id=None,
                service_name=f"{ref.service_name} (copy)",
                base_url=ref.base_url,
                description=ref.description,
                auth_type=ref.auth_type,
                keychain_key_name="",
                label_ids=list(ref.label_ids),
            ),
        )
        self.refresh()

    def _open_dialog(self, ref: ApiRef | None) -> None:
        is_edit = ref is not None
        name_field = ft.TextField(
            label="Nama service",
            value=ref.service_name if ref else "",
            dense=True,
        )
        url_field = ft.TextField(
            label="Base URL",
            value=ref.base_url if ref else "",
            dense=True,
        )
        desc_field = ft.TextField(
            label="Deskripsi",
            value=ref.description if ref else "",
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        auth_field = ft.Dropdown(
            label="Tipe Auth",
            value=ref.auth_type if ref else "",
            options=[
                ft.dropdown.Option(""),
                ft.dropdown.Option("Bearer Token"),
                ft.dropdown.Option("API Key"),
                ft.dropdown.Option("Basic Auth"),
                ft.dropdown.Option("OAuth2"),
                ft.dropdown.Option("None"),
            ],
            dense=True,
        )
        keychain_field = ft.TextField(
            label="Nama key di Keychain",
            value=ref.keychain_key_name if ref else "",
            dense=True,
        )
        secret_field = ft.TextField(
            label="Secret value (disimpan di Keychain)",
            password=True,
            can_reveal_password=True,
            dense=True,
        )
        if is_edit and ref and ref.keychain_key_name:
            existing_secret = get_secret(ref.keychain_key_name)
            if existing_secret:
                secret_field.value = existing_secret

        all_labels = labels_repo.list_labels(self.conn)
        current_label_ids = ref.label_ids if ref else []
        label_checks, label_section = build_label_checkboxes(
            all_labels, current_label_ids
        )

        def _save(e: Any) -> None:
            selected_ids = get_selected_label_ids(label_checks)
            keychain_name = (keychain_field.value or "").strip()
            if is_edit and ref:
                ref.service_name = (name_field.value or "").strip()
                ref.base_url = (url_field.value or "").strip()
                ref.description = desc_field.value or ""
                ref.auth_type = auth_field.value or ""
                ref.keychain_key_name = keychain_name
                ref.label_ids = selected_ids
                api_refs_repo.update_api_ref(self.conn, ref)
            else:
                api_refs_repo.create_api_ref(
                    self.conn,
                    ApiRef(
                        id=None,
                        service_name=(name_field.value or "").strip(),
                        base_url=(url_field.value or "").strip(),
                        description=desc_field.value or "",
                        auth_type=auth_field.value or "",
                        keychain_key_name=keychain_name,
                        label_ids=selected_ids,
                    ),
                )
            if keychain_name:
                if secret_field.value:
                    store_secret(keychain_name, secret_field.value)
                else:
                    from src.core.secrets import delete_secret
                    try:
                        delete_secret(keychain_name)
                    except Exception:
                        pass
            self.page.pop_dialog()
            self.refresh()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit API Reference" if is_edit else "Tambah API Reference"),
            content=ft.Column(
                [
                    name_field,
                    url_field,
                    desc_field,
                    auth_field,
                    keychain_field,
                    secret_field,
                    label_section,
                ],
                spacing=8,
                tight=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            actions=[
                ft.TextButton("Batal", on_click=lambda e: self.page.pop_dialog()),
                ft.FilledButton("Simpan", on_click=_save),
            ],
        )
        self.page.show_dialog(dialog)

    def _delete(self, ref: ApiRef) -> None:
        def _confirm(e: Any) -> None:
            api_refs_repo.delete_api_ref(self.conn, ref.id)  # type: ignore[arg-type]
            self.page.pop_dialog()
            self.refresh()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Hapus API reference?"),
            content=ft.Text(f'"{ref.service_name}" akan dihapus.'),
            actions=[
                ft.TextButton("Batal", on_click=lambda e: self.page.pop_dialog()),
                ft.FilledButton(
                    "Hapus",
                    bgcolor=PALETTE["state.danger"],
                    on_click=_confirm,
                ),
            ],
        )
        self.page.show_dialog(dialog)

    def refresh(self) -> None:
        refs = api_refs_repo.list_api_refs(self.conn)
        refs = self.sort_items(refs, "service_name")
        self.list_area.controls.clear()

        if not refs:
            self.list_area.controls.append(
                self.empty_state("Belum ada API reference. Tambahkan yang pertama!")
            )
        else:
            for r in refs:
                self.list_area.controls.append(self._item_card(r))
        self.page.update()

    def _item_card(self, ref: ApiRef) -> ft.Container:
        secret_value = get_secret(ref.keychain_key_name or ref.service_name)
        labels = labels_repo.get_labels_for_item(
            self.conn, "api_refs", ref.id  # type: ignore[arg-type]
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                ref.service_name,
                                size=16,
                                weight=ft.FontWeight.W_600,
                                color=PALETTE["text.primary"],
                            ),
                            ft.Container(expand=True),
                            copy_button(
                                ft.Icons.CONTENT_COPY,
                                "Copy URL",
                                lambda: copy_to_clipboard(
                                    self.page,
                                    ref.base_url or ref.service_name,
                                    f'URL "{ref.service_name}" disalin!',
                                ),
                                accent=False,
                            ),
                            copy_button(
                                ft.Icons.KEY_OUTLINED,
                                "Copy key",
                                lambda: copy_to_clipboard(
                                    self.page,
                                    secret_value or ref.service_name,
                                    f'API key "{ref.service_name}" disalin!',
                                ),
                                accent=True,
                            ),
                            action_button(
                                ft.Icons.COPY_ALL_OUTLINED,
                                "Duplicate",
                                lambda e, r=ref: self._duplicate(r),
                            ),
                            action_button(
                                ft.Icons.EDIT_OUTLINED,
                                "Edit",
                                lambda e, r=ref: self._open_edit(r),
                            ),
                            action_button(
                                ft.Icons.DELETE_OUTLINE,
                                "Hapus",
                                lambda e, r=ref: self._delete(r),
                                danger=True,
                            ),
                        ],
                        spacing=4,
                    ),
                    render_label_chips(labels),
                    ft.Text(
                        ref.base_url,
                        size=12,
                        color=PALETTE["accent.mint"],
                        style=ft.TextStyle(font_family="monospace"),
                    ),
                    ft.Container(
                        content=ft.Text(
                            ref.auth_type or "Tanpa auth",
                            size=11,
                            color=PALETTE["text.secondary"],
                        ),
                        bgcolor=PALETTE["bg.surface-hover"],
                        padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                        border_radius=6,
                    ),
                ],
                spacing=4,
            ),
            bgcolor=PALETTE["bg.surface"],
            border=ft.Border.all(1, PALETTE["border.subtle"]),
            border_radius=8,
            padding=12,
            on_hover=lambda e: _hover_card(e),
        )


def _hover_card(e: ft.ControlEvent) -> None:
    """Efek hover pada kartu."""
    ctrl = e.control
    if e.data == "true":
        ctrl.bgcolor = PALETTE["bg.surface-hover"]  # type: ignore[attr-defined]
        ctrl.update()
    else:
        ctrl.bgcolor = PALETTE["bg.surface"]  # type: ignore[attr-defined]
        ctrl.update()

from admin_interface.models import Theme

# Hapus tema lama jika ada
Theme.objects.all().delete()

# Buat tema Django default
theme = Theme.objects.create(
    name='Django Default',
    active=True,
    title='SOC Dashboard',
    title_color='#F5DD5D',
    title_visible=True,
    logo_color='#1C1C1C',
    logo_visible=True,
    css_header_background_color='#0C4B33',
    css_header_text_color='#F5DD5D',
    css_header_link_color='#F5DD5D',
    css_header_link_hover_color='#FFFFFF',
    css_module_background_color='#F8F8F8',
    css_module_text_color='#1C1C1C',
    css_module_link_color='#0C4B33',
    css_module_link_hover_color='#1C1C1C',
    css_module_rounded_corners=True,
    css_generic_link_color='#0C4B33',
    css_generic_link_hover_color='#1C4B33',
    css_save_button_background_color='#0C4B33',
    css_save_button_background_hover_color='#1C4B33',
    css_save_button_text_color='#FFFFFF',
    css_delete_button_background_color='#BA2121',
    css_delete_button_background_hover_color='#A41515',
    css_delete_button_text_color='#FFFFFF',
    list_filter_dropdown=True,
    related_modal_active=True,
    related_modal_background_color='#000000',
    related_modal_background_opacity='0.7',
    related_modal_rounded_corners=True,
    related_modal_close_button=True,
    env_name='SOC',
    env_visible_in_header=True,
    env_visible_in_favicon=True,
    language_chooser_active=False,
)

print(f'✅ Theme created: {theme.name}')
exit()

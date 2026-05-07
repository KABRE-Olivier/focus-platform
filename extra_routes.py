
@app.route('/profile')
def profile():
    user = get_current_user()
    if user is None:
        session.clear()
        return redirect(url_for('login'))
    from attestation_focus import ensure_tables, check_all_modules_completed, issue_global_attestation, get_user_certs_detail
    ensure_tables()
    all_completed, completed_count, total_count = check_all_modules_completed(user['id'])
    progress = get_user_module_progress(user['id'])
    certs = get_user_certs_detail(user['id'])
    cert_map = {c['module_id']: c for c in certs}
    all_badges_list = get_all_badges()
    earned = get_user_badges(user['id'])
    earned_ids = [b['id'] for b in earned]
    uid = issue_global_attestation(user['id']) if all_completed else None
    return render_template('profile.html', user=user,
        all_completed=all_completed, completed_count=completed_count,
        total_count=total_count, progress=progress, cert_map=cert_map,
        all_badges=all_badges_list, earned_badges=earned,
        earned_badge_ids=earned_ids, attestation_uid=uid)

@app.route('/attestation/download')
def download_attestation():
    user = get_current_user()
    if user is None:
        return redirect(url_for('login'))
    from attestation_focus import ensure_tables, check_all_modules_completed, issue_global_attestation, generate_attestation_pdf
    ensure_tables()
    all_done, _, _ = check_all_modules_completed(user['id'])
    if not all_done:
        flash('Complete tous les modules.', 'warning')
        return redirect(url_for('profile'))
    uid = issue_global_attestation(user['id'])
    pdf = generate_attestation_pdf(user['id'], uid)
    return send_file(pdf, as_attachment=True, download_name='Attestation_FOCUS.pdf')

